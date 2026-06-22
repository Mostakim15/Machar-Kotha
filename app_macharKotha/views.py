from django.shortcuts import render
from rest_framework import generics


# Create your views here.
def home(request):
    return render(request, 'app_macharKotha/home.html')