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
    HttpResponseServerError,
    HttpResponseNotAllowed
)

import cassy

logger = logging.getLogger('plantalytics_backend.admin')


def verify_admin(admin_username, auth_token):
    """
    Verifies username has admin privileges and is authenticated.
    """

    try:
        message = (
            'Validating {} is an authenticated admin.'
        ).format(admin_username)
        logger.info(message)
        is_admin = cassy.verify_authenticated_admin(admin_username, auth_token)
        if (is_admin is False):
            return False
        message = (
            'Successfully validated {} is an authenticated admin.'
        ).format(admin_username)
        logger.info(message)
        return True
    except Exception as e:
        raise e


@csrf_exempt
def user_info(request):
    """
    Endpoint returns the user info for the requested username.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    admin_username = str(data.get('admin_username', ''))
    request_username = str(data.get('request_username', ''))

    try:
        is_verified = verify_admin(admin_username, auth_token)
        if (is_verified is False):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            '{} is retrieving user info for username: {}.'
        ).format(admin_username, request_username)
        logger.info(message)
        response = cassy.get_user_info(request_username)
        message = (
            '{} successfully retrieved user info for username: {}.'
        ).format(admin_username, request_username)
        logger.info(message)
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
def user_new(request):
    """
    Endpoint creates a new user with the requested user info.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    admin_username = str(data.get('admin_username', ''))
    new_user_info = data.get('new_user_info', '')
    new_username = str(new_user_info.get('username', ''))

    try:
        is_verified = verify_admin(admin_username, auth_token)
        if (is_verified is False):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            '{} is attemping to create new user: {}.'
        ).format(admin_username, new_username)
        logger.info(message)
        cassy.create_new_user(new_user_info)
        message = (
            '{} successfully created new user: {}.'
        ).format(admin_username, new_username)
        logger.info(message)
        body = {
                'errors': {}
        }
        return HttpResponse(
            json.dumps(body),
            content_type='application/json'
        )
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
def user_subscription(request):
    """
    Endpoint update the subscription end date for the requested user.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    admin_username = str(data.get('admin_username', ''))
    request_username = str(data.get('request_username', ''))
    sub_end_date = str(data.get('sub_end_date', ''))

    try:
        is_verified = verify_admin(admin_username, auth_token)
        if (is_verified is False):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            '{} is attemping to update subscription for user: {}.'
        ).format(admin_username, request_username)
        logger.info(message)
        cassy.update_user_subscription(request_username, sub_end_date)
        message = (
            '{} successfully updated subscruption for user: {}.'
        ).format(admin_username, request_username)
        logger.info(message)
        body = {
                'errors': {}
        }
        return HttpResponse(
            json.dumps(body),
            content_type='application/json'
        )
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
def user_edit(request):
    """
    Endpoint edits the user for the requested username.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    admin_username = str(data.get('admin_username', ''))
    user_edit_info = data.get('edit_user_info', '')
    username = str(user_edit_info.get('username', ''))

    try:
        is_verified = verify_admin(admin_username, auth_token)
        if (is_verified is False):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            '{} is attemping to edit info for user: {}.'
        ).format(admin_username, username)
        logger.info(message)
        cassy.edit_user(user_edit_info)
        message = (
            '{} successfully edited info for user: {}.'
        ).format(admin_username, username)
        logger.info(message)
        body = {
                'errors': {}
        }
        return HttpResponse(
            json.dumps(body),
            content_type='application/json'
        )
    except PlantalyticsException as e:
        message = (
            'Error attempting to edit user info. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except Exception as e:
        message = (
            'Unknown error occurred while attempting to edit user info:'
        )
        logger.exception(message)
        error = custom_error(UNKNOWN, str(e))
        return HttpResponseServerError(error, content_type='application/json')


@csrf_exempt
def user_disable(request):
    """
    Endpoint disables the user for the requested username.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    admin_username = str(data.get('admin_username', ''))
    request_username = str(data.get('request_username', ''))

    try:
        is_verified = verify_admin(admin_username, auth_token)
        if (is_verified is False):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            '{} is attemping to disable user: {}.'
        ).format(admin_username, request_username)
        logger.info(message)
        cassy.disable_user(request_username)
        message = (
            '{} successfully disabled user: {}.'
        ).format(admin_username, request_username)
        logger.info(message)
        body = {
                'errors': {}
        }
        return HttpResponse(
            json.dumps(body),
            content_type='application/json'
        )
    except PlantalyticsException as e:
        message = (
            'Error attempting to disable user. Error code: {}'
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
def vineyard_info(request):
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
        is_verified = verify_admin(admin_username, auth_token)
        if (is_verified is False):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            '{} is retrieving vineyard info for vineyard id: {}.'
        ).format(admin_username, vineyard_id)
        logger.info(message)
        response = cassy.get_vineyard_info(vineyard_id)
        message = (
            '{} successfully retrieved vineyard info for vineyard id: {}.'
        ).format(admin_username, vineyard_id)
        logger.info(message)
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


@csrf_exempt
def vineyard_edit(request):
    """
    Endpoint edits the vineyard info for the requested vineyard id.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    admin_username = str(data.get('admin_username', ''))
    edit_vineyard_info = data.get('edit_vineyard_info', '')
    vineyard_id = str(edit_vineyard_info.get('vineyard_id', ''))

    try:
        is_verified = verify_admin(admin_username, auth_token)
        if (is_verified is False):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            '{} is attemping to edit info for vineyard id: {}.'
        ).format(admin_username, vineyard_id)
        logger.info(message)
        cassy.edit_vineyard(edit_vineyard_info)
        message = (
            '{} successfully edited info for vineyard id: {}.'
        ).format(admin_username, vineyard_id)
        logger.info(message)
        body = {
                'errors': {}
        }
        return HttpResponse(
            json.dumps(body),
            content_type='application/json'
        )
    except PlantalyticsException as e:
        message = (
            'Error attempting to edit vineyard info. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except Exception as e:
        message = (
            'Unknown error occurred while attempting '
            'to edit vineyard info:'
        )
        logger.exception(message)
        error = custom_error(UNKNOWN, str(e))
        return HttpResponseServerError(error, content_type='application/json')


@csrf_exempt
def vineyard_new(request):
    """
    Endpoint creates a new vineyard with the requested user info.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    admin_username = str(data.get('admin_username', ''))
    new_vineyard_info = data.get('new_vineyard_info', '')
    vineyard_id = str(new_vineyard_info.get('vineid', ''))

    try:
        is_verified = verify_admin(admin_username, auth_token)
        if (is_verified is False):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            '{} is attemping to create new vineyard with vineyard id: {}.'
        ).format(admin_username, vineyard_id)
        logger.info(message)
        cassy.create_new_vineyard(new_vineyard_info)
        message = (
            '{} successfully created new vineyard with vineyard id: {}.'
        ).format(admin_username, vineyard_id)
        logger.info(message)
        body = {
                'errors': {}
        }
        return HttpResponse(
            json.dumps(body),
            content_type='application/json'
        )
    except PlantalyticsException as e:
        message = (
            'Error attempting to create new vineyard. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except Exception as e:
        message = (
            'Unknown error occurred while attempting to create new vineyard:'
        )
        logger.exception(message)
        error = custom_error(UNKNOWN, str(e))
        return HttpResponseServerError(error, content_type='application/json')


@csrf_exempt
def vineyard_disable(request):
    """
    Endpoint disables the vineyard for the requested vineyard id.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    admin_username = str(data.get('admin_username', ''))
    vineyard_id = str(data.get('vineyard_id', ''))

    try:
        is_verified = verify_admin(admin_username, auth_token)
        if (is_verified is False):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            '{} is attemping to disable vineyard with vineyard id: {}.'
        ).format(admin_username, vineyard_id)
        logger.info(message)
        response = cassy.disable_vineyard(vineyard_id)
        message = (
            '{} successfully disabled vineyard with vineyard id: {}.'
        ).format(admin_username, vineyard_id)
        logger.info(message)
        body = {
                'errors': {}
        }
        return HttpResponse(
            json.dumps(body),
            content_type='application/json'
        )
    except PlantalyticsException as e:
        message = (
            'Error attempting to disable vineyard. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except Exception as e:
        message = (
            'Unknown error occurred while attempting to disable vineyard:'
        )
        logger.exception(message)
        error = custom_error(UNKNOWN, str(e))
        return HttpResponseServerError(error, content_type='application/json')