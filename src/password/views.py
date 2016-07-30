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

    '''
    username = data.get('username', '')
    new_password = data.get('password', '')
    old_password = data.get('old', '')
    auth_token = data.get('token', '')
    '''
    return HttpResponse()

@csrf_exempt
def reset(request):
    return HttpResponse()
