from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

bev_choices = (("C", "Coffee"), ("T", "Tea"), ("L", "Lemonade"), ("G", "GreenTea"), ("Null", "Null"))


class Inventory(models.Model):  # creating a model for inventory which will have fields id,item name and quantity
    item_name = models.CharField(max_length=25, null=False)
    quantity = models.PositiveSmallIntegerField(default=0)


class Order(models.Model):  # creating a model for orders which will have fields id,user id,order time and pending(flag)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    order_time = models.DateTimeField(auto_now=True)
    pending = models.BooleanField(default=False)

    class Meta:
        ordering = ('order_time',)  # the model will be ordered on the basis of order_time


# creating a model for beverages which will have fields id, user id, morning beverages and evening beverages
class Beverages(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    morning_bev = models.CharField(choices=bev_choices, default="C", max_length=2)
    evening_bev = models.CharField(choices=bev_choices, default="T", max_length=2)


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
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ('order_id',)
