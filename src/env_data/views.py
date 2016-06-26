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
from django.http import HttpResponse, HttpResponseForbidden

import cassy


def index(request):
    """
    Access database to response with requested environmental mapping data.
    """

    vineyard_id = request.GET['vineyard_id']
    env_variable = request.GET['env_variable']
    response = {}
    map_data = []

    try:
        coordinates = cassy.get_node_coordinates(vineyard_id)

        # Build data structure to return as JSON response content.
        for coordinate in coordinates:
            value = cassy.get_env_data(coordinate['node_id'], env_variable)
            map_data_point = {
                'latitude':coordinate['lat'],
                'longitude':coordinate['lon'],
                env_variable:value
            }
            map_data.append(map_data_point)
        response['env_data'] = map_data
        return HttpResponse(json.dumps(response), content_type='application/json')
    except Exception as e:
        return HttpResponseForbidden
