from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_201_CREATED, HTTP_200_OK, HTTP_409_CONFLICT)
from rest_framework.response import Response
from .models import Inventory, Order, Bookings, Beverages, ItemBook
from .serializers import InventorySerializer, BeverageSerializer, BookingSerializer, OrderSerializer, ItemBookSerializer
from rest_framework.views import APIView
from datetime import date, datetime, timedelta
import xlsxwriter
import pandas as pd
from django.http import HttpResponse
import boto3


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'}, status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)

    return Response({'token': token.key}, status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def register(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    if username is None or email is None:
        return Response({'error': 'Please provide both username and email'}, status=HTTP_400_BAD_REQUEST)
    else:
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return Response({'error': 'Username or Email already exists'}, status=HTTP_409_CONFLICT)
        else:
            User.objects.create_user(username, email, password)
            user = authenticate(username=username, password=password)
            use = User.objects.filter(username=user).first()
            token, _ = Token.objects.get_or_create(user=user)
            data = {'user_id': use.id, 'morning_bev': '3', 'evening_bev': '4'}
            serializer = BeverageSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': "success"}, status=HTTP_200_OK)
            return Response({'error': serializer.errors}, status=HTTP_409_CONFLICT)


class GenerateReport(APIView):
    def get(self, request):
        #response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        #response['Content-Disposition'] = "attachment; filename=report.xlsx"
        workbook = xlsxwriter.Workbook('report.xlsx', {'in_memory': True})
        s3_resource = boto3.resource('s3')
        worksheet = workbook.add_worksheet('summary')
        bold = workbook.add_format({'bold': True, 'align': 'center'})
        nothing = workbook.add_format({'align': 'center', 'underline': True})
        user_headings = workbook.add_format({'align': 'center', 'underline': True, 'bold': True, 'border' : True, 'bg_color': 'red'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yy', 'bold': True, 'align': 'center', 'border': True})
        worksheet.write('A2', 'Users', bold)
        query_bev = Beverages.objects.all()
        start_time = query_bev.order_by('timestamp').first().timestamp.date()
        q2 = query_bev.order_by('user_id_id', 'timestamp')
        query_slot = Bookings.objects.all()
        q3 = query_slot.order_by('user_id_id', 'day_book')
        query_order = Order.objects.all()
        q4 = query_order.order_by('user_id_id', 'order_time')
        col = 1
        for dates in pd.bdate_range(start_time, date.today()):
            worksheet.merge_range(1, col, 1, col + 3, dates.date(), date_format)
            worksheet.write(2, col, "Slot", bold)
            worksheet.write(2, col+1, "Orders", bold)
            worksheet.write(2, col+2, "Morning", bold)
            worksheet.write(2, col+3, "Evening", bold)
            col += 4
        last_user = " "
        col = 3
        row = 2
        work = {}
        for query in q2:
            cols = 1
            if last_user != str(query.user_id):
                row += 1
                last_user = str(query.user_id)
                work[last_user] = workbook.add_worksheet(last_user)
                work[last_user].merge_range(1, cols+3, 1, cols + 9, last_user.upper(), user_headings)
                worksheet.write(row, 0, 'internal:%s!A1' % last_user, nothing, last_user)
                for dates in pd.bdate_range(start_time, date.today()):
                    work[last_user].write('A1', 'internal:summary!A1', nothing, 'summary')
                    work[last_user].merge_range(3, cols, 3, cols + 3, dates.date(), date_format)
                    work[last_user].write(4, cols, "Slot", bold)
                    work[last_user].write(4, cols+1, "Orders", bold)
                    work[last_user].write(4, cols+2, "Morning", bold)
                    work[last_user].write(4, cols+3, "Evening", bold)
                    cols += 4
            last_date = query.timestamp.date()
            for dates in pd.bdate_range(start_time, date.today()):
                if dates.date() >= last_date:
                    worksheet.write(row, col, query.morning_bev)
                    worksheet.write(row, col+1, query.evening_bev)
                    work[last_user].write(5, col, query.morning_bev)
                    work[last_user].write(5, col+1, query.evening_bev)
                col += 4
            col = 3

        last_user = " "
        col = 1
        row = 2
        cols = col
        last_date = start_time
        for query in q3:
            col = cols
            if last_user != str(query.user_id):
                row += 1
                col = 1
                last_user = str(query.user_id)
                last_date = start_time
            for dates in pd.bdate_range(last_date, date.today()):
                if dates.date() == query.day_book:
                    worksheet.write(row, col, query.slot_id_id)
                    work[last_user].write(5, col, query.slot_id_id)
                    last_date = query.day_book + timedelta(days=1)
                    cols = col + 4
                else:
                    worksheet.write(row, col, "NA")
                    work[last_user].write(5, col, "NA")
                col += 4
        last_user = " "
        col = 2
        row = 3
        cols = col
        res = []
        last_date = start_time
        sid = q4.first().user_id_id
        for query in q4:
            col = cols
            if query.order_time.date() == last_date - timedelta(days=1):
                col -= 4
                last_date = query.order_time.date()
            if last_user != str(query.user_id):
                num = query.user_id_id
                row += num - sid
                sid = num
                col = 2
                last_user = str(query.user_id)
                last_date = start_time
                res = []
            for dates in pd.bdate_range(last_date, date.today()):
                if dates.date() == query.order_time.date():
                    res.append(str(query.id))
                    worksheet.write(row, col, str(res))
                    work[last_user].write(5, col, str(res))
                    last_date = query.order_time.date() + timedelta(days=1)
                    cols = col + 4
                else:
                    worksheet.write(row, col, "NA")
                    work[last_user].write(5, col, "NA")
                col += 4

        workbook.close()
        #s3 = boto3.client('s3')
        #s3.generate_presigned_url('put_object', Params={'Bucket':'generatingreports', 'Key':'report.xlsx'}, ExpiresIn=600)
        first_object = s3_resource.Object(bucket_name='generatingreports', key='report.xlsx')
        first_object.upload_file('report.xlsx',ExtraArgs={'ACL':'public-read'})
        bucket_location = boto3.client('s3').get_bucket_location(Bucket='generatingreports')
        object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(bucket_location['LocationConstraint'],'generatingreports','report.xlsx')
        return Response({"message":"Report generated","code":"201 CREATED","url":object_url})


class TheBeverage(APIView):
    @csrf_exempt
    def get_object(self, user):
        try:
            return Beverages.objects.filter(user_id=user.id).last()
        except Beverages.DoesNotExist:
            raise HTTP_404_NOT_FOUND

    def get(self, request):
        current_user = request.user
        beverages = self.get_object(current_user)
        serializer = BeverageSerializer(beverages)
        return Response({'morning_bev': serializer.data['morning_bev'], 'evening_bev': serializer.data['evening_bev']},
                        status=HTTP_200_OK)

    @csrf_exempt
    def put(self, request):
        current_user = request.user
        morning = request.data.get('morning_bev')
        evening = request.data.get('evening_bev')
        data = {'user_id': current_user.id, 'morning_bev': morning, 'evening_bev': evening}
        serializer = BeverageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class TheInventory(APIView):
    def get(self):
        try:
            inventory = Inventory.objects.all()
        except Inventory.DoesNotExist:
            raise HTTP_404_NOT_FOUND
        result = [ ]
        for item in inventory:
            serializer = InventorySerializer(item)
            result.append(serializer.data)
        return Response({"Inventory": result}, status=HTTP_200_OK)


class TheOrders(APIView):
    @csrf_exempt
    def get_object(self, user):
        try:
            return Order.objects.filter(user_id=user.id)
        except Order.DoesNotExist:
            return Response({"message": "No order Exist"}, status=HTTP_404_NOT_FOUND)

    def get(self, request):
        current_user = request.user
        orders = self.get_object(current_user)
        result = []
        res = []
        for order in orders:
            serializer = OrderSerializer(order)
            orderid = serializer.data['id']
            items = ItemBook.objects.filter(order_id=orderid)
            for item in items:
                serial = ItemBookSerializer(item)
                res.append(serial.data)
            result.append(res)
            res=[]
        return Response({"Orders": result}, status=HTTP_200_OK)

    @csrf_exempt
    def post(self, request):
        current_user = request.user
        order_data = request.data.get("OrderItems")
        data = {'user_id':current_user.id, 'order_time':datetime.utcnow().time(),'pending':True}
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            for item in order_data:
                item_id = item["item_id"]
                quantity = int(item["quantity"])
                try:
                    it = Inventory.objects.get(id=item_id)
                    seri= InventorySerializer(it)
                except Inventory.DoesNotExist:
                    raise HTTP_404_NOT_FOUND
                if int(seri.data['quantity'])>=quantity:
                    data_order = {'order_id':serializer.data['id'],'item_id':item_id, 'quantity': quantity}
                    serial=ItemBookSerializer(data=data_order)
                    if serial.is_valid():
                        serial.save()
                        data_new = {'item_name':seri.data['item_name'], 'quantity': int(seri.data['quantity']) - quantity}
                        ser = InventorySerializer(it,data=data_new)
                        if ser.is_valid():
                            ser.save()
                        else:
                            return Response(ser.errors,status=HTTP_400_BAD_REQUEST)
                    else:
                        return Response(serial.errors, status=HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": "Not enough items for order in inventory"}, status=HTTP_200_OK)
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class TheBookings(APIView):
    @csrf_exempt
    def get_object(self, user):
        try:
            return Bookings.objects.get(user_id=user.id, day_book=date.today())
        except Bookings.DoesNotExist:
            return None

    def get(self, request):
        current_user = request.user
        booking = self.get_object(current_user)
        result = Bookings.objects.filter(day_book=date.today())
        slots = [8, 8, 8, 8]
        for item in result:
            ser = BookingSerializer(item)
            slots[ser.data["slot_id"] - 1] -= 1
        if booking is None:
            return Response({"Slots": slots}, status=HTTP_200_OK)
        else:
            serializer = BookingSerializer(booking)
            return Response({"booking": serializer.data, "slots": slots}, status=HTTP_200_OK)

    @csrf_exempt
    def post(self, request):
        current_user = request.user
        booking = self.get_object(current_user)
        if booking is None:
            slot_id = request.data.get('slot_id')
            result = Bookings.objects.filter(day_book=date.today())
            slot = [8, 8, 8, 8]
            for item in result:
                ser = BookingSerializer(item)
                slot[ser.data["slot_id"] - 1] -= 1
            if slot[int(slot_id)-1] > 0:
                data = {'user_id': current_user.id, 'slot_id': slot_id, 'day_book': date.today()}
                serializer = BookingSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message": "Slot acquired"}, status=HTTP_201_CREATED)
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
            return Response({"message": "new slot not available"}, status=HTTP_409_CONFLICT)
        else:
            return Response({"message": "Already Added"}, status=HTTP_409_CONFLICT)

    @csrf_exempt
    def put(self, request):
        current_user = request.user
        booking = self.get_object(current_user)
        if booking is None:
            return Response({"message": "Select a slot first"}, status=HTTP_400_BAD_REQUEST)
        else:
            slot_id = request.data.get('slot_id')
            result = Bookings.objects.filter(day_book=date.today())
            slot = [8, 8, 8, 8]
            for item in result:
                ser = BookingSerializer(item)
                slot[ser.data["slot_id"] - 1] -= 1
            if slot[int(slot_id)-1]>0:
                data = {"user_id": current_user.id, "slot_id": slot_id, "day_book": date.today()}
                serializer = BookingSerializer(booking, data=data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"message": "Slot updated"}, status=HTTP_200_OK)
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
            return Response({"message": "new slot not available"}, status=HTTP_409_CONFLICT)
