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

from common.exceptions import PlantalyticsException
from common.errors import *
from django.views.decorators.csrf import csrf_exempt
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotAllowed
)

import cassy

logger = logging.getLogger('plantalytics_backend.vineyard')


@csrf_exempt
def index(request):
    """
    Accesses database to respond with requested vineyard metadata.
    """

    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))
    vineyard_id = str(data.get('vineyard_id', ''))
    auth_token = str(data.get('auth_token', ''))

    try:
        message = (
            'Validating auth token for vineyard id {}.'
        ).format(vineyard_id)
        logger.info(message)

        cassy.verify_auth_token(auth_token)
    except PlantalyticsException as e:
        message = (
            'Invalid auth token for vineyard id {}'
        ).format(vineyard_id)
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except Exception as e:
        message = (
            'Error occurred while auth token for vineyard id {}{}{}.'
        ).format(vineyard_id, '\n', str(e))
        logger.exception(message)
        error = custom_error(AUTH_UNKNOWN, str(e))
        return HttpResponseForbidden(error, content_type='application/json')

    try:
        message = (
            'Fetching vineyard data for vineyard id {}.'
        ).format(vineyard_id)
        logger.info(message)

        coordinates = cassy.get_vineyard_coordinates(vineyard_id)

        message = (
            'Successfully fetched vineyard data for vineyard id {}.'
        ).format(vineyard_id)
        logger.info(message)

        response = {
            'center': coordinates[0],
            'boundary': coordinates[1]
        }
        return HttpResponse(
            json.dumps(response),
            content_type='application/json'
        )
    except PlantalyticsException as e:
        message = (
            'Invalid vineyard ID while fetching vineyard data: {}'
        ).format(vineyard_id)
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseBadRequest(error, content_type='application/json')
    except Exception as e:
        message = (
            'Error occurred while fetching vineyard data for '
            'vineyard id {}. {}'
        ).format(vineyard_id, str(e))
        logger.exception(message)
        error = custom_error(VINEYARD_UNKNOWN, str(e))
        return HttpResponseBadRequest(error, content_type='application/json')
