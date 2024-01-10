from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import uuid
from flight.models import DBPilots


def login_(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/flight/airlineflight')
        else:
            return redirect('/user/registration')
    else:
        return render(request, 'login.html')


def registration_(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = User.objects.create_user(username, password=password)
        user.save()
        pilot = DBPilots(id=user.id,
                         id_users=uuid.uuid4())
        pilot.save()
        return redirect('/user/login')
    return render(request, 'registration.html')


def logout_(request):
    logout(request)
    return redirect('/user/login')
