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

    try:
        # Get stored password from database, and verify with password arg
        logger.info('Fetching password for user \'' + username + '\'.')
        stored_password = cassy.get_user_password(username)
        logger.info('Successfully fetched password for user \''
                    + username + '\'.'
        )

        if stored_password == submitted_password:
            # Generate token and put into JSON object
            token = str(uuid.uuid4())
            token_object = {}

            # Return response with token object
            if username != os.environ.get('LOGIN_USERNAME'):
                logger.info('Storing auth token for user \''
                    + username + '\'.'
                )
                cassy.set_user_auth_token(
                    username,
                    submitted_password,
                    token
                )
                logger.info('Retrieving auth token for user \''
                    + username + '\'.'
                )
                token_object['token'] = cassy.get_user_auth_token(
                    username,
                    submitted_password
                )
            else:
                cassy.set_user_auth_token(
                    username,
                    submitted_password,
                    os.environ.get('LOGIN_SEC_TOKEN')
                )
                token_object['token'] = cassy.get_user_auth_token(
                    username,
                    submitted_password
                )
            logger.info('Successfully logged in user \''
                + username + '\'.'
            )
            return HttpResponse(json.dumps(token_object), content_type='application/json')
        else:
            logger.warning('Incorrect password supplied for user \''
                           + username + '\'.'
            )
            return HttpResponseForbidden()
    except Exception as e:
        logger.exception('Error occurred while fetching password for user \''
                    + username + ' \'.'
                    + str(e)
        )
        return HttpResponseForbidden()
