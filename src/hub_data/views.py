#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

import os
import json
import logging

from common.exceptions import *
from common.errors import *
from django.views.decorators.csrf import csrf_exempt
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotAllowed
)

import cassy

logger = logging.getLogger('plantalytics_backend.hub_data')


@csrf_exempt
def index(request):
    """
    Receive data from hub to insert into database.
    """

    allowed_methods = ['POST', 'PUT']
    if request.method not in (allowed_methods):
        return HttpResponseNotAllowed(allowed_methods)

    data = json.loads(request.body.decode("utf-8"))
    hub_key = str(data.get('key', ''))
    hub_id = str(data.get('hub_id', ''))

    try:
        message = (
            'Validating key for hub id \'{}\'.'
        ).format(hub_id)
        logger.info(message)
        if hub_key != os.environ.get('HUB_KEY'):
            raise PlantalyticsHubException(HUB_KEY_INVALID)

        logger.info('Inserting hub data.')
        cassy.store_env_data(data)
        logger.info('Successfully inserted hub data.')
        return HttpResponse()
    except PlantalyticsException as e:
        message = (
            'Error attempting to process hub data. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except Exception as e:
        message = (
            'Error occurred while inserting hub data for hub id \'{}\'. {}'
        ).format(hub_id, str(e))
        logger.exception(message)
        return HttpResponseBadRequest()
