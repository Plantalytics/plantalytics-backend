#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

import json

from django.shortcuts import render
from django.http import HttpResponse

import cassy


def index(request, vineyard_id, env_variable):
    """
    Access database to response with requested environmental mapping data.
    """

    response = {}
    map_data = []
    coordinates = cassy.get_node_coordinates(vineyard_id)

    # Build data structure to return as JSON response content.
    for coordinate in coordinates:
        value = cassy.get_env_data(coordinate['node_id'], env_variable)
        map_data_point = {"latitude":coordinate['lat'], "longitude":coordinate['lon'], env_variable:value}
        map_data.append(map_data_point)
    response["env_data"] = map_data
    return HttpResponse(json.dumps(response), content_type="application/json")