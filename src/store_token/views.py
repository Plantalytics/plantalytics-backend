#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

import logging

from common.errors import *
from common.exceptions import *
from django.http import HttpResponse, HttpResponseForbidden

import cassy

logger = logging.getLogger('plantalytics_backend.store_token')


def index(request):
    """
    Endpoint to return 'success' HTTP status after storing user security token
    if correct user/pass are passed in.
    """
    username = request.GET.get('username', '')
    submitted_password = request.GET.get('password', '')
    securty_token = request.GET.get('securitytoken', '')

    try:
        # Get stored password from database, and verify with password arg
        logger.info('Fetching password for user \'' + username + '\'.')
        stored_password = cassy.get_user_password(username)
        logger.info(
            'Successfully fetched password for user \''
            + username + '\'.'
        )
        if stored_password == submitted_password:
            try:
                # Store security token into database
                logger.info('Storing security token for user \'' + username + '\'.')
                cassy.set_user_auth_token(username, submitted_password, securty_token)
                logger.info(
                    'Successfully stored security token for user \''
                    + username + '\'.'
                )
                # Return 'success' HTTP response
                return HttpResponse(status=200)
            except PlantalyticsException as e:
                logger.exception(
                    'Error occurred while storing security token for user \''
                    + username + ' \'.'
                    + str(e)
                )
                error = custom_error(str(e))
                return HttpResponseForbidden(error, content_type='application/json')
        else:
            logger.warning(
                'Incorrect password supplied for user \''
                + username + '\'.'
            )
            error = custom_error(LOGIN_ERROR)
            return HttpResponseForbidden(error, content_type='application/json')
    except PlantalyticsException as e:
        logger.warn('Invalid username. Error code: ' + str(e))
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except Exception as e:
        logger.exception(
            'Error occurred while fetching password for user \''
            + username + ' \'.'
            + str(e)
        )
        error = custom_error(AUTH_UNKNOWN, str(e))
        return HttpResponseForbidden(error, content_type='application/json')
