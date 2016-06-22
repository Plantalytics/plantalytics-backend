from django.shortcuts import render
from django.http import HttpResponse

import cassy
import json
import random


def index(request, vineyard_id, env_variable):
    """
    Access database to response with requested environmental data.
    """

    # Fetch data.
    response_dict = {}
    response_records = []
    coordinates = cassy.get_node_coordinates(vineyard_id)
    for coordinate in coordinates:
        value = cassy.get_env_data(coordinate['node_id'], env_variable)
        record = {"latitude":coordinate['lat'], "longitude":coordinate['lon'], env_variable:value}
        response_records.append(record)
    response_dict["env_data"] = response_records
    return HttpResponse(json.dumps(response_dict), content_type="application/json")
