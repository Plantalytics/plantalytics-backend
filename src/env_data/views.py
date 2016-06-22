from django.shortcuts import render
from django.http import HttpResponse

import cassy
import json
import random


def index(request, vineyard_id, env_variable):
    """
    Access database to response with requested environmental data.
    """

    results = cassy.get_env_data(vineyard_id, env_variable)
    response_dict = {}
    response_records = []

    # Generated random coordinates until database is sorted out.
    for row in results:
        lat = random.uniform(0, 90)
        lon = random.uniform(0, 180)
        value = row
        record = {"latitude":lat, env_variable:value, "longitude":lon}
        response_records.append(record)
    response_dict["env_data"] = response_records

    return HttpResponse(json.dumps(response_dict), content_type="application/json")
