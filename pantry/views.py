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
from datetime import date, datetime


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
                return Response({'message':"success"},status=HTTP_200_OK)
            return Response({'error':serializer.errors}, status=HTTP_409_CONFLICT)


class TheBeverage(APIView):
    @csrf_exempt
    def get_object(self, user):
        try:
            return Beverages.objects.get(user_id=user.id)
        except Beverages.DoesNotExist:
            raise HTTP_404_NOT_FOUND

    @csrf_exempt
    def get(self, request):
        current_user = request.user
        beverages = self.get_object(current_user)
        serializer = BeverageSerializer(beverages)
        return Response({'morning_bev': serializer.data['morning_bev'], 'evening_bev': serializer.data['evening_bev']},
                        status=HTTP_200_OK)

    @csrf_exempt
    def put(self, request):
        current_user = request.user
        beverage = self.get_object(current_user)
        morning = request.data.get('morning_bev')
        evening = request.data.get('evening_bev')
        data = {'user_id': current_user.id, 'morning_bev': morning, 'evening_bev': evening}
        serializer = BeverageSerializer(beverage, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=HTTP_400_BAD_REQUEST)


class TheInventory(APIView):
    @csrf_exempt
    def get(self,request):
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

    @csrf_exempt
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
                            pass
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

    @csrf_exempt
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
            slot_id=request.data.get('slot_id')
            data = {'user_id': current_user.id, 'slot_id': slot_id, 'day_book': date.today()}
            serializer = BookingSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Slot acquired"}, status=HTTP_201_CREATED)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Already Added"},status=HTTP_409_CONFLICT)

    @csrf_exempt
    def put(self, request):
        current_user = request.user
        booking=self.get_object(current_user)
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
