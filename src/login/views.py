#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

import os
import uuid
import json
import logging

from common.exceptions import PlantalyticsException
from common.errors import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden

import cassy

logger = logging.getLogger('plantalytics_backend.login')


@csrf_exempt
def index(request):
    """
    Mock auth endpoint to return success with generated token
    if valid username and password pair is passed in.
    """

    data = json.loads(request.body.decode("utf-8"))
    username = str(data.get('username', ''))
    submitted_password = str(data.get('password', ''))

    try:
        # Get stored password from database, and verify with password arg
        message = (
            'Fetching password for user \'{}\'.'
        ).format(username)
        logger.info(message)

        stored_password = cassy.get_user_password(username)

        message = (
            'Successfully fetched password for user \'{}\'.'
        ).format(username)
        logger.info(message)

        if stored_password == submitted_password:
            # Generate token and put into JSON object
            response_object = {
                'auth_token': str(uuid.uuid4()),
            }
            # Return response with token object
            if username != os.environ.get('LOGIN_USERNAME'):
                message = (
                    'Storing auth token for user \'{}\'.'
                ).format(username)
                logger.info(message)

                cassy.set_user_auth_token(
                    username,
                    submitted_password,
                    response_object['auth_token']
                )

                message = (
                    'Retrieving auth token for user \'{}\'.'
                ).format(username)
                logger.info(message)
            # Condition it coupled to unit tests
            # TODO: Uncouple unit tests and refactor
            else:
                response_object['auth_token'] = os.environ.get('LOGIN_SEC_TOKEN')

            # Add in vineyard ids
            response_object['authorized_vineyards'] = cassy.get_authorized_vineyards(
                username
            )

            message = (
                'Successfully logged in user \'{}\'.'
            ).format(username)
            logger.info(message)
            return HttpResponse(
                json.dumps(response_object),
                content_type='application/json'
            )
        else:
            message = (
                'Incorrect password supplied for user \'{}\'.'
            ).format(username)
            logger.warning(message)
            error = custom_error(LOGIN_ERROR)
            return HttpResponseForbidden(
                error,
                content_type='application/json'
            )
    # Invalid username -- expected exception
    except PlantalyticsException as e:
        message = (
            'Unknown username \'{}\'.'
        ).format(username)
        logger.warning(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    # Unexpected exception
    except Exception as e:
        message = (
            'Error occurred while fetching password for user \'{}\'. {}'
        ).format(username, str(e))
        logger.exception(message)
        error = custom_error(LOGIN_UNKNOWN, str(e))
        return HttpResponseForbidden(error, content_type='application/json')
