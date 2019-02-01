from django.urls import path
from .views import login,pending,register,Beverage

urlpatterns=[
    path('login',login),
    path('register', register),
    path('pending',pending),
    #path('beverages/', Beverage.as_view()),
]