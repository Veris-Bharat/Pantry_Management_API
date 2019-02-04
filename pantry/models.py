from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

bev_choices = (("3", "3"), ("4", "4"), ("7", "7"), ("8", "8"))


class Inventory(models.Model):
    item_name = models.CharField(max_length=25,null=False)
    quantity = models.PositiveSmallIntegerField(default=0)


class Order(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    order_time = models.DateTimeField(auto_now=True)
    pending = models.BooleanField(default=False)

    class Meta:
        ordering = ('order_time',)


class Beverages(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    morning_bev = models.CharField(choices=bev_choices, default="3", max_length=2)
    evening_bev = models.CharField(choices=bev_choices, default="4", max_length=2)


class Slots(models.Model):
    slot_start_time = models.TimeField(auto_now=False)
    slot_end_time = models.TimeField(auto_now=False)


class Bookings(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    slot_id = models.ForeignKey(Slots, on_delete=models.CASCADE)
    day_book = models.DateField(default=datetime.now)

    class Meta:
        ordering = ('day_book',)

class ItemBook(models.Model):
    order_id = models.ForeignKey(Order,on_delete=models.CASCADE)
    item_id = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ('order_id',)
