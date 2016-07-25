#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

import json
import logging

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

import cassy

logger = logging.getLogger('plantalytics_backend.env_data')


def index(request):
    """
    Access database to respond with requested environmental mapping data.
    """

    vineyard_id = request.GET.get('vineyard_id', '')
    env_variable = request.GET.get('env_variable', '')
    securitytoken = request.GET.get('securitytoken', '')
    response = {}
    map_data = []

    try:
        logger.info(
            'Validating securitytoken token for vineyard id \''
            + vineyard_id + '\'.'
        )
        cassy.verify_auth_token(securitytoken)
    except Exception as e:
        logger.exception('Error occurred while security token for '
                    + 'vineyard id \'' + vineyard_id + ' \'.'
                    + str(e)
        )
        return HttpResponseForbidden()

    try:
        logger.info('Fetching ' + env_variable + ' data.')
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

        logger.info('Successfully fetched ' + env_variable
                    + ' data for vineyard ' + vineyard_id + '.'
        )
        return HttpResponse(json.dumps(response), content_type='application/json')
    except Exception as e:
        logger.exception('Error occurred while fetching ' + env_variable
                    + ' data for vineyard ' + vineyard_id + '.'
                    + str(e)
        )
        return HttpResponseBadRequest()
