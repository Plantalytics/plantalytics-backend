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

from common.exceptions import *
from common.errors import *
from django.http import HttpResponse, HttpResponseBadRequest

import cassy

logger = logging.getLogger('plantalytics_backend.env_data')


def index(request):
    """
    Access database to respond with requested environmental mapping data.
    """
    vineyard_id = request.GET.get('vineyard_id', '')
    env_variable = request.GET.get('env_variable', '')
    response = {}
    map_data = []
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

        logger.info(
            'Successfully fetched ' + env_variable
            + ' data for vineyard ' + vineyard_id + '.'
        )
        return HttpResponse(json.dumps(response), content_type='application/json')
    except PlantalyticsException as e:
        logger.warn('Invalid vineyard_id or env_variable. Error code: ' + str(e))
        error = custom_error(str(e))
        return HttpResponseBadRequest(error, content_type='application/json')
    except Exception as e:
        logger.exception(
            'Error occurred while fetching ' + env_variable
            + ' data for vineyard ' + vineyard_id + '.'
            + str(e)
        )
        error = custom_error(ENV_DATA_UNKNOWN, str(e))
        return HttpResponseBadRequest(error, content_type='application/json')
