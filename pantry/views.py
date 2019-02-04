from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.http import HttpResponse, JsonResponse
from rest_framework.status import (HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND,HTTP_201_CREATED, HTTP_200_OK, HTTP_409_CONFLICT)
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from .models import Inventory, Order, Bookings, Beverages, Slots
from .serializers import InventorySerializer, BeverageSerializer, BookingSerializer, OrderSerializer#, SlotSerializer
from django.views import View
from rest_framework.views import APIView
from datetime import date


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

"""
@csrf_exempt
@api_view(["GET"])
def pending(request):

    current_user = request.user
    pend = Order.objects.filter(user_id=current_user.id)
    return Response(pend, status=HTTP_200_OK)
"""


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
            return Order.objects.get(user_id=user.id)
        except Order.DoesNotExist:
            raise HTTP_404_NOT_FOUND

    @csrf_exempt
    def get(self, request):
        current_user = request.user
        order = self.get_object(current_user)
        result = []
        for item in order:
            serializer = OrderSerializer(item)
            result.append(serializer.data)
        return Response({"Orders": result}, status=HTTP_200_OK)

    @csrf_exempt
    def post(self, request):
        current_user = request.user
        item_id = []
        quantity = []
        for item in request.data:
            item_id.append(item['item_id'])
            quantity.append(item['quantity'])

            serializer = OrderSerializer()
        if serializer.is_valid():
            serializer.save()
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
