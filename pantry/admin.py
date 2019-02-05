from django.contrib import admin
from .models import Inventory, Order, Beverages, Slots, Bookings, ItemBook

admin.site.register(Inventory)
admin.site.register(Order)
admin.site.register(Beverages)
admin.site.register(Bookings)
admin.site.register(Slots)
admin.site.register(ItemBook)
