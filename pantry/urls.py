from django.urls import path
from .views import login, pending, register, TheInventory, TheOrders

urlpatterns=[
    path('login', login),
    path('register', register),
    path('pending', pending),
    path('inventory/', TheInventory.as_view()),
    path('order/', TheOrders.as_view()),
]