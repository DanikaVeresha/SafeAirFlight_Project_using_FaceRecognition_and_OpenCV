from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_, name='login_'),
    path('registration', views.registration_, name='registration_'),
    path('logout', views.logout_, name='logout_'),
]

