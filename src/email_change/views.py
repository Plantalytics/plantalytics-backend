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

from common.exceptions import *
from common.errors import *
from django.views.decorators.csrf import csrf_exempt
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
    HttpResponseServerError
)

import cassy

logger = logging.getLogger('plantalytics_backend.email')


def email_is_good(new_email):
    result = True
    # TODO: Logic for checking if email address is acceptable
    return result


@csrf_exempt
def index(request):
    """
    Access database to change email address.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    new_email = str(data.get('email, '''))
    logger.info('Request to change email address.')
    if auth_token and new_email:
        if email_is_good(new_email) is not True:
            return HttpResponseBadRequest()
        try:
            username = cassy.verify_auth_token(auth_token)

        except PlantalyticsException as e:
            logger.warn('Invalid auth token.')
            error = custom_error(str(e))
            return HttpResponseForbidden(error, content_type='application/json')

        try:
            cassy.change_user_email(username, new_email)
        except PlantalyticsException as e:
            logger.warn('Error changing email address.')
            error = custom_error(str(e))
            return HttpResponseBadRequest(error, content_type='application/json')
        except Exception as e:
            logger.exception('Error in attempt to change email address for {}'.format(username))
            error = custom_error(CHANGE_EMAIL_UNKNOWN)
            return HttpResponseServerError(error)

    else:
        logger.warn('Missing auth token ({}) or email address({}).'.format(auth_token, new_email))
        error_code = AUTH_NO_TOKEN if auth_token == '' else EMAIL_INVALID
        error = custom_error(error_code)
        return HttpResponseBadRequest(error, content_type='application/json')

    return HttpResponse()
