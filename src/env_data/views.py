from django.shortcuts import render
from django.http import HttpResponse

import cassy

# Create your views here.

def index(request):
    result = cassy.get_env_data()
    return HttpResponse(result)
