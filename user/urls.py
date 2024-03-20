from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_, name='login_'),
    path('registration', views.registration_, name='registration_'),
    path('logout', views.logout_, name='logout_'),
    path('get', views.get_routs_list_pilot, name='get_routs_list_pilot'),
    path('back', views.back, name='back')
]

