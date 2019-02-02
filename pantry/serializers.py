from rest_framework import serializers
from pantry.models import Beverages,Order,Inventory,Slots,Bookings,bev_choices


class BeverageSerializer(serializers.ModelSerializer):
    #id = serializers.IntegerField(read_only=True)
    #morning_bev = serializers.ChoiceField(choices=bev_choices, default="3")
    #evening_bev = serializers.ChoiceField(choices=bev_choices, default="4")
    class Meta:
        model = Beverages
        fields = ('morning_bev', 'evening_bev')

    #def create(self, validated_data):
    #    return Beverages.objects.create(**validated_data)

    #def update(self, instance, validated_data):
     #   instance.morning_bev = validated_data.get('morning_bev', instance.morning_bev)
      #  instance.evening_bev = validated_data.get('evening_bev', instance.evening_bev)
      #  instance.save()
      #  return instance


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ('id', 'item_name', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id', 'user_id', 'item_id', 'quantity', 'order_time', 'pending')


class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slots
        fields: ('id', 'slot_start_time', 'slot_end_time')


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = ('id', 'user_id', 'slot_id', 'day_book')
