from rest_framework import serializers
from pantry.models import Beverages,Order,Inventory,Bookings,ItemBook


class BeverageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beverages
        fields = ('user_id', 'morning_bev', 'evening_bev')


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ('id', 'item_name', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'user_id', 'order_time', 'pending')


class ItemBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemBook
        #fields: ('order_id', 'item_id', 'quantity')
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = ('id', 'user_id', 'slot_id', 'day_book')
