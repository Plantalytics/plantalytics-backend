from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse("Hello, Plantalytics World!! Welcome to the backend, where things ain't pretty, but they get stuff DONE!")
