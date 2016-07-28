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
import uuid

import cassy
from common.exceptions import PlantalyticsException
from common.errors import *
from django.http import HttpResponse, HttpResponseForbidden

logger = logging.getLogger('plantalytics_backend.login')


def index(request):
    """
    Mock auth endpoint to return success with generated token
    if correct user/pass are passed in.
    """
    username = request.GET.get('username', '')
    submitted_password = request.GET.get('password', '')

    # Generate token and put into JSON object
    token = str(uuid.uuid4())
    token_object = {'token': token}

    try:
        # Get stored password from database, and verify with password arg
        logger.info('Fetching password for user \'' + username + '\'.')
        stored_password = cassy.get_user_password(username)
        logger.info(
            'Successfully fetched password for user \''
            + username + '\'.'
        )

        if stored_password == submitted_password:
            # Return response with token object
            return HttpResponse(json.dumps(token_object), content_type='application/json')
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
