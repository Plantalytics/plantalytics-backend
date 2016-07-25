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

from common.errors import custom_error
from common.exceptions import *
from django.http import HttpResponse, HttpResponseForbidden

import cassy

logger = logging.getLogger('plantalytics_backend.validate')


def index(request):
    """
    Endpoint to return success with stored security token
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
            try:
                # Get stored security token from database
                logger.info('Fetching security token for user \'' + username + '\'.')
                stored_token = cassy.get_user_auth_token(username, submitted_password)
                logger.info('Successfully fetched security token for user \''
                            + username + '\'.'
                            )
                # Return response with security token object
                return HttpResponse(json.dumps(stored_token), content_type='application/json')
            except Exception as e:
                logger.exception('Error occurred while fetching security token for user \''
                                 + username + ' \'.'
                                 + str(e)
                                 )
                error = custom_error('auth_err', str(e))
                return HttpResponseForbidden(error, content_type='application/json')
        else:
            logger.warning('Incorrect password supplied for user \''
                           + username + '\'.'
                           )
            error = custom_error('login_err')
            return HttpResponseForbidden(error, content_type='application/json')
    except PlantalyticsException as e:
        logger.warn('Invalid username: ' + username)
        error = custom_error('login_err')
        return HttpResponseForbidden(error, content_type='application/json')
    except Exception as e:
        logger.exception('Error occurred while fetching password for user \''
                         + username + ' \'.'
                         + str(e)
                         )
        error = custom_error('unknown', str(e))
        return HttpResponseForbidden(error, content_type='application/json')
