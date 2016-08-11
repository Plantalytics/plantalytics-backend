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

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from common.exceptions import PlantalyticsException
from common.errors import *
from django.http import HttpResponse, HttpResponseForbidden

import cassy

logger = logging.getLogger('plantalytics_backend.login')

@csrf_exempt
def index(request):
    """
    Mock auth endpoint to return success with generated token
    if correct user/pass are passed in.
    """

    data = json.loads(request.body.decode("utf-8"))
    username = data.get('username', '')
    submitted_password = data.get('password', '')

    try:
        # Get stored password from database, and verify with password arg
        logger.info('Fetching password for user \'' + username + '\'.')
        stored_password = cassy.get_user_password(username)
        logger.info(
            'Successfully fetched password for user \''
            + username + '\'.'
        )

        if stored_password == submitted_password:
            # Generate token and put into JSON object
            auth_token = str(uuid.uuid4())
            response_object = {}

            # Return response with token object
            if username != os.environ.get('LOGIN_USERNAME'):
                logger.info('Storing auth token for user \''
                    + username + '\'.'
                )
                cassy.set_user_auth_token(
                    username,
                    submitted_password,
                    auth_token
                )
                logger.info('Retrieving auth token for user \''
                    + username + '\'.'
                )
            else:
                cassy.set_user_auth_token(
                    username,
                    submitted_password,
                    os.environ.get('LOGIN_SEC_TOKEN')
                )
            response_object['auth_token'] = cassy.get_user_auth_token(
                username,
                submitted_password
            )
            response_object['vineyard_ids'] = cassy.get_authorized_vineyards(
                username
            )
            logger.info('Successfully logged in user \''
                + username + '\'.'
            )
            return HttpResponse(json.dumps(response_object), content_type='application/json')
        else:
            logger.warning('Incorrect password supplied for user \''
                           + username + '\'.'
                           )
            error = custom_error(LOGIN_ERROR)
            return HttpResponseForbidden(error, content_type='application/json')

    # Invalid username -- expected exception
    except PlantalyticsException as e:
        logger.warning('Unknown username \''
                       + username + '\'.')
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    # Unexpected exception
    except Exception as e:
        logger.exception('Error occurred while fetching password for user \''
                         + username + ' \'.'
                         + str(e)
                         )
        error = custom_error(LOGIN_UNKNOWN, str(e))
        return HttpResponseForbidden(error, content_type='application/json')
