from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.http import HttpResponse, JsonResponse
from rest_framework.status import (HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_409_CONFLICT)
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from .models import Inventory, Order, Bookings, Beverages, Slots
from .serializers import InventorySerializer, BeverageSerializer, BookingSerializer, OrderSerializer, SlotSerializer
from django.views import View


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
            data={'morning_bev':'3','evening_bev':'4'}
            serializer = BeverageSerializer(use,data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':"success"},status=HTTP_200_OK)
            return Response({'error':serializer.errors}, status=HTTP_409_CONFLICT)


@csrf_exempt
@api_view(["GET"])
def pending(request):
    current_user = request.user
    pend = Order.objects.filter(user_id=current_user.id, pending=True)
    return Response(pend, status=HTTP_200_OK)

"""
@csrf_exempt
class TheBeverage(View):
    def get(self, request):
        current_user = request.user
        bev = Beverages.objects.filter(user_id=current_user.id)
        if bev:
            return Response({'Morning':bev.morning_bev, 'Evening': bev.evening_bev}, status=HTTP_200_OK)
        else:
            return Response({'error': 'No user'}, status=HTTP_400_BAD_REQUEST)

    def put(self, request):
        morning = request.data.get('morning_bev')
        evening = request.data.get('evening_bev')
        current_user = request.user
        bev = Beverages.objects.filter(user_id=current_user.id)
        if bev:
            pass
        else:
            return Response({'error': 'No user'}, status=HTTP_400_BAD_REQUEST)
"""



class TheInventory(View):
    @csrf_exempt
    def get(self, request):
        inventory=Inventory.objects.all()
        serializer = InventorySerializer(inventory,many=True)
        return JsonResponse(serializer.data, safe=False)

    @csrf_exempt
    def post(self,request):
        data = JSONParser().parse(request)
        serializer = InventorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)



class TheOrders(View):
    @csrf_exempt
    def get(self, request):
        current_user=request.user
        try:
            order = Order.objects.get(user_id=current_user.id)
            serializer = OrderSerializer(order)
            return JsonResponse(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'No user'}, status=HTTP_400_BAD_REQUEST)

    @csrf_exempt
    def post(self,request):
        current_user = request.user
        try:
            users = User.objects.get(id=current_user.id)
        except User.DoesNotExist:
            return Response({'error': 'No user'}, status=HTTP_400_BAD_REQUEST)
        data = JSONParser().parse(request)
        serializer = OrderSerializer(users, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    @csrf_exempt
    def delete(self, request):
        current_user = request.user
        try:
            order = Order.objects.get(user_id=current_user.id)
            serializer = OrderSerializer(order)
            return JsonResponse(serializer.data)
        except Order.DoesNotExist:
            return Response({'error': 'No user'}, status=HTTP_400_BAD_REQUEST)
        order.delete()
        return HttpResponse(status=204)

