from django.shortcuts import render
from django.http import HttpResponse

import cassy

# Create your views here.

def index(request, vineyard_id, variable_id):
    result = cassy.get_env_data(vineyard_id, variable_id)
    return HttpResponse(result)
