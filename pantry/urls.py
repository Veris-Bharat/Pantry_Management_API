from django.urls import path
from .views import login, register, TheInventory, TheOrders, TheBeverage, TheBookings, GenerateReport, GetURL

urlpatterns = [
    path('login', login),
    path('register', register),
    path('inventory/', TheInventory.as_view()),
    path('order/', TheOrders.as_view()),
    path('beverages/', TheBeverage.as_view()),
    path('bookings/', TheBookings.as_view()),
    path('generatereport/', GenerateReport.as_view()),
    path('geturl/',GetURL.as_view()),
]
