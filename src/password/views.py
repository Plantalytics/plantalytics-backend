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
from django.views.decorators.csrf import csrf_exempt
from common.exceptions import PlantalyticsException
from common.errors import *
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest

logger = logging.getLogger('plantalytics_backend.login')


@csrf_exempt
def change(request):
    """
    Mock auth endpoint to return success with generated token
    if correct user/pass are passed in.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest()

    data = json.loads(request.body.decode('utf-8'))

    username = data.get('username', '')
    new_password = data.get('password', '')
    old_password = data.get('old', '')
    auth_token = data.get('token', '')

    return HttpResponse()

@csrf_exempt
def reset(request):
    """
    Endpoint to email a password reset token to the requested user.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest()

    data = json.loads(request.body.decode('utf-8'))
    username = data.get('username', '')

    try:
        email_object = {}
        email_object['email'] = cassy.get_user_email(username)
        return HttpResponse(json.dumps(email_object), content_type='application/json')
    # Invalid username -- expected exception
    except PlantalyticsException as e:
        logger.warning('Unknown username \''
                       + username + '\'.')
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    # Unexpected exception
    except Exception as e:
        logger.exception('Error occurred while fetching email for user \''
                         + username + ' \'.'
                         + str(e)
                         )
        error = custom_error(EMAIL_ERROR, str(e))
        return HttpResponseForbidden(error, content_type='application/json')


    return HttpResponse()
