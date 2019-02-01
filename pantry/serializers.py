from rest_framework import serializers
from .models import Beverages,Order,Inventory,Slots,Bookings

class BeveragesSerializer(serializers.Serializer):
    id