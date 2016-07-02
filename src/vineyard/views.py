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
from django.http import HttpResponse, HttpResponseBadRequest

import cassy


def index(request):
    """
    Access database to respond with requested vineyard metadata.
    """
    vineyard_id = request.GET.get('vineyard_id', '')
    response = {}

    try:
        coordinates = cassy.get_vineyard_coordinates(vineyard_id)
        response['center'] = coordinates[0]
        response['boundary'] = coordinates[1]
        return HttpResponse(json.dumps(response), content_type='application/json')
    except Exception as e:
        return HttpResponseBadRequest()
