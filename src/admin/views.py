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
    HttpResponseForbidden,
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseNotAllowed
)

import cassy

logger = logging.getLogger('plantalytics_backend.admin')


@csrf_exempt
def user(request):
    """
    Endpoint returns the user info for the request username.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    admin_username = str(data.get('admin_username', ''))
    request_username = str(data.get('request_username', ''))

    try:
        is_admin = cassy.verify_authenticated_admin(admin_username, auth_token)
        if(is_admin is False):
            return HttpResponseForbidden()
        response = cassy.get_user_info(request_username)
        return HttpResponse(
            json.dumps(response),
            content_type='application/json'
        )
    except PlantalyticsException as e:
        message = (
            'Error attempting to retireve user info. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except Exception as e:
        message = (
            'Unknown error occurred while attempting to retrieve user info:'
        )
        logger.exception(message)
        error = custom_error(UNKNOWN, str(e))
        return HttpResponseServerError(error, content_type='application/json')


@csrf_exempt
def new(request):
    """
    Endpoint creates a new user with the requested user info.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    admin_username = str(data.get('admin_username', ''))
    new_user_info = data.get('new_user_info', '')

    try:
        is_admin = cassy.verify_authenticated_admin(admin_username, auth_token)
        if(is_admin is False):
            return HttpResponseForbidden()
        cassy.create_new_user(new_user_info)
        return HttpResponse()
    except PlantalyticsException as e:
        message = (
            'Error attempting to create new user. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except Exception as e:
        message = (
            'Unknown error occurred while attempting to create new user:'
        )
        logger.exception(message)
        error = custom_error(UNKNOWN, str(e))
        return HttpResponseServerError(error, content_type='application/json')


@csrf_exempt
def subscription(request):
    """
    Endpoint update the subscription end date for the requested user.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    admin_username = str(data.get('admin_username', ''))
    request_username = str(data.get('request_username', ''))
    sub_end_date = data.get('sub_end_date', '')

    try:
        is_admin = cassy.verify_authenticated_admin(admin_username, auth_token)
        if(is_admin is False):
            return HttpResponseForbidden()
        cassy.update_user_subscription(request_username, sub_end_date)
        return HttpResponse()
    except PlantalyticsException as e:
        message = (
            'Error attempting to update user subscription. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except Exception as e:
        message = (
            'Unknown error occurred while attempting '
            'to update user subscription:'
        )
        logger.exception(message)
        error = custom_error(UNKNOWN, str(e))
        return HttpResponseServerError(error, content_type='application/json')


@csrf_exempt
def disable(request):
    """
    Endpoint disables the user for the request username.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    admin_username = str(data.get('admin_username', ''))
    request_username = str(data.get('request_username', ''))

    try:
        is_admin = cassy.verify_authenticated_admin(admin_username, auth_token)
        if(is_admin is False):
            return HttpResponseForbidden()
        response = cassy.disable_user(request_username)
        return HttpResponse()
    except PlantalyticsException as e:
        message = (
            'Error attempting to disable. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except Exception as e:
        message = (
            'Unknown error occurred while attempting to disable user:'
        )
        logger.exception(message)
        error = custom_error(UNKNOWN, str(e))
        return HttpResponseServerError(error, content_type='application/json')


@csrf_exempt
def vineyard(request):
    """
    Endpoint returns the vineyard info for the requested vineyard id.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    admin_username = str(data.get('admin_username', ''))
    vineyard_id = str(data.get('vineyard_id', ''))

    try:
        is_admin = cassy.verify_authenticated_admin(admin_username, auth_token)
        if(is_admin is False):
            return HttpResponseForbidden()
        response = cassy.get_vineyard_info(vineyard_id)
        return HttpResponse(
            json.dumps(response),
            content_type='application/json'
        )
    except PlantalyticsException as e:
        message = (
            'Error attempting to retireve vineyard info. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except Exception as e:
        message = (
            'Unknown error occurred while attempting '
            'to retrieve vineyard info:'
        )
        logger.exception(message)
        error = custom_error(UNKNOWN, str(e))
        return HttpResponseServerError(error, content_type='application/json')
