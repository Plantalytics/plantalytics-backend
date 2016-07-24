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

logger = logging.getLogger('plantalytics_backend.vineyard')


def index(request):
    """
    Access database to respond with requested vineyard metadata.
    """
    vineyard_id = request.GET.get('vineyard_id', '')
    securitytoken = request.GET.get('securitytoken', '')
    response = {}

    try:
        logger.info('Validating securitytoken token for vineyard id \'' + vineyard_id + '\'.')
        cassy.verify_auth_token(securitytoken)
    except Exception as e:
        logger.exception('Error occurred while security token for '
                    + 'vineyard id \'' + vineyard_id + ' \'.'
                    + str(e)
        )
        return HttpResponseForbidden()

    try:

        logger.info('Fetching vineyard data for vineyard id \'' + vineyard_id + '\'.')
        coordinates = cassy.get_vineyard_coordinates(vineyard_id)
        logger.info('Successfully fetched vineyard data for vineyard id \'' + vineyard_id + '\'.')

        response['center'] = coordinates[0]
        response['boundary'] = coordinates[1]
        return HttpResponse(json.dumps(response), content_type='application/json')
    except Exception as e:
        logger.exception('Error occurred while fetching vineyard data for '
                    + 'vineyard id \'' + vineyard_id + ' \'.'
                    + str(e)
        )
        return HttpResponseBadRequest()
