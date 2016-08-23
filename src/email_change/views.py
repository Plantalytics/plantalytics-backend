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
import re

from common.exceptions import *
from common.errors import *
from django.core.mail import send_mail
from django.conf import settings
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
    return True if re.match(r"[^@]+@[^@]+\.[^@]+", new_email) else False


@csrf_exempt
def index(request):
    """
    Access database to change email address.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    new_email = str(data.get('new_email', ''))
    logger.info('Request to change email address.')
    if auth_token and new_email:
        if email_is_good(new_email) is not True:
            logger.warn("Invalid email address: {}".format(new_email))
            error = custom_error(EMAIL_INVALID)
            return HttpResponseBadRequest(
                error,
                content_type='application/json'
            )
        try:
            username = cassy.verify_auth_token(auth_token)

        except PlantalyticsException as e:
            logger.warn('Invalid auth token.')
            error = custom_error(str(e))
            return HttpResponseForbidden(
                error,
                content_type='application/json'
            )

        try:
            old_email = cassy.get_user_email(username)
            cassy.change_user_email(username, new_email)
            message = (
                'The email address associated with this account '
                'has been changed to:\n{}\n\n If you did not request '
                'this change, please contact us as admin@plantalytics.us\n'
            ).format(new_email)
            send_mail(
                'Plantalytics Email Changed',
                message,
                settings.EMAIL_HOST_USER,
                [old_email],
                fail_silently=False,
            )

        except PlantalyticsException as e:
            logger.warn('Error changing email address.')
            error = custom_error(str(e))
            return HttpResponseBadRequest(
                error,
                content_type='application/json'
            )
        except Exception as e:
            message = (
                'Error in attempt to change email address for {}'
            ).format(username)
            logger.exception(message)
            error = custom_error(CHANGE_EMAIL_UNKNOWN)
            return HttpResponseServerError(error)

    else:
        message = (
            'Missing auth token ({}) or email address({}).'
        ).format(auth_token, new_email)
        logger.warn(message)
        error_code = AUTH_NO_TOKEN if auth_token == '' else EMAIL_INVALID
        error = custom_error(error_code)
        return HttpResponseBadRequest(error, content_type='application/json')
    body = {'errors': {}}
    return HttpResponse(json.dumps(body), content_type='application/json')
