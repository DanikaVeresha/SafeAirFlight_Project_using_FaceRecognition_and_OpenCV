from django.urls import path
from . import views

urlpatterns = [
    path('airlineflight', views.airflight, name='airflight'),
    path('manualcontrolrequest', views.manual_control_request, name='manual_control_request'),
]
