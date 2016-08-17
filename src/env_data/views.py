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
import time
import datetime

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

logger = logging.getLogger('plantalytics_backend.env_data')


def check_hubs_not_reporting(latest_times):
    """
    Checks if the most recent hub batch times haven't reported in
    more than 20 minutes.
    """

    timestamp_format = "%Y-%m-%d %H:%M:%S"
    current_epoch_time = time.strftime(
        timestamp_format,
        time.gmtime(time.time())
    )
    current_timestamp = datetime.datetime.strptime(
        current_epoch_time,
        timestamp_format
    )
    current_unix_timestamp = time.mktime(current_timestamp.timetuple())

    for timestamp in latest_times:
        batch_time = timestamp.lasthubbatchsent
        batch_unix_time = time.mktime(batch_time.timetuple())
        time_elapsed = (
            int(current_unix_timestamp - batch_unix_time) / 60
        )
        if(time_elapsed > 20):
            return False
    return True


@csrf_exempt
def index(request):
    """
    Access database to respond with requested environmental mapping data.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    request_data = json.loads(request.body.decode('utf-8'))
    auth_token = str(request_data.get('auth_token', ''))
    vineyard_id = request_data.get('vineyard_id', '')
    env_variable = str(request_data.get('env_variable', ''))

    try:
        message = (
            'Validating auth token token for vineyard id {}.'
        ).format(str(vineyard_id))
        logger.info(message)
        cassy.verify_auth_token(auth_token)
    except Exception as e:
        message = (
            'Error occurred while auth token for vineyard id {}. {}'
        ).format(str(vineyard_id), str(e))
        logger.exception(message)
        return HttpResponseForbidden()

    try:
        message = (
            'Fetching {} data.'
        ).format(env_variable)
        logger.info(message)

        # Check most recent hub batch timestamp
        message = (
            'Checking latest hub batch times.'
        )
        logger.info(message)
        latest_times = cassy.check_latest_batch_time(vineyard_id)
        hubs_are_reporting = check_hubs_not_reporting(latest_times)
        if(hubs_are_reporting is False):
            message = (
                'A hub for vineyard id {} has not reported in the last 20 min.'
            ).format(str(vineyard_id))
            logger.warn(message)

        coordinates = cassy.get_node_coordinates(vineyard_id)

        # Build data structure to return as JSON response content.
        map_data = []
        for coordinate in coordinates:
            value = cassy.get_env_data(
                coordinate['node_id'],
                env_variable
            )
            map_data_point = {
                'latitude': coordinate['lat'],
                'longitude': coordinate['lon'],
                env_variable: value,
            }
            map_data.append(map_data_point)
        response = {
            'env_data': map_data,
        }

        message = (
            'Successfully fetched {} data for vineyard id {}.'
        ).format(env_variable, str(vineyard_id))
        logger.info(message)
        return HttpResponse(
            json.dumps(response),
            content_type='application/json'
        )
    except PlantalyticsException as e:
        message = (
            'Invalid vineyard_id or env_variable. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseBadRequest(error, content_type='application/json')
    except Exception as e:
        message = (
            'Error occurred while fetching {} data for vineyard id {}. {}'
        ).format(env_variable, str(vineyard_id), str(e))
        logger.exception(message)
        error = custom_error(ENV_DATA_UNKNOWN, str(e))
        return HttpResponseBadRequest(error, content_type='application/json')
