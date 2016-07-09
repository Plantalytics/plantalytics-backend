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

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden

import cassy

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
    token_object = {}
    token_object['token'] = token

    try:
        # Get stored password from database, and verify with password arg
        logger.info('Fetching password for user \'' + username + '\'.')
        stored_password = cassy.get_user_password(username)
        logger.info('Successfully fetched password for user \''
                    + username + '\'.'
        )

        if stored_password == submitted_password:
            # Return response with token object
            return HttpResponse(json.dumps(token_object), content_type='application/json')
        else:
            logger.warning('Incorrect password supplied for user \''
                           + username + '\'.'
            )
            return HttpResponseForbidden()
    except Exception as e:
        logger.error('Error occurred while fetching password for user \''
                    + username + ' \'.'
                    + str(e)
        )
        return HttpResponseForbidden()
