from rest_framework import serializers
from pantry.models import Beverages,Order,Inventory,Slots,Bookings


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
        fields = ('id', 'user_id', 'item_id', 'quantity', 'order_time', 'pending')


"""class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slots
        fields: ('id', 'slot_start_time', 'slot_end_time')
"""


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = ('id', 'user_id', 'slot_id', 'day_book')
