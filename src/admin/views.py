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
import datetime
import time
import string

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


def verify_admin(auth_token):
    """
    Verifies username has admin privileges and is authenticated.
    """

    try:
        message = (
            'Validating user is an authenticated admin.'
        )
        logger.info(message)
        is_admin = cassy.verify_authenticated_admin(auth_token)
        if (is_admin is False):
            return False
        message = (
            'Successfully validated user is an authenticated admin.'
        )
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
    request_username = str(data.get('request_username', ''))

    try:
        if not verify_admin(auth_token):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            'Retrieving user info for username: {}.'
        ).format(request_username)
        logger.info(message)
        response = cassy.get_user_info(request_username)
        message = (
            'Successfully retrieved user info for username: {}.'
        ).format(request_username)
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


def check_user_id(user_id):
    """
    Validates submitted user id by checking if it already exists.
    """

    try:
        message = (
            'Validating submitted user id.'
        )
        logger.info(message)
        if user_id != '':
            invalid = (

                int(user_id) < 0 or
                cassy.check_user_id_exists(int(user_id))
            )
            if (invalid):
                raise PlantalyticsDataException(USER_ID_INVALID)
        message = (
            'Submitted user id successfully validated.'
        )
        logger.info(message)
    except PlantalyticsException as e:
        raise e
    except ValueError as e:
        raise e
    except Exception as e:
        raise e


def check_username(username):
    """
    Validates submitted username by checking if it already exists.
    """

    try:
        message = (
            'Validating submitted username.'
        )
        logger.info(message)
        invalid = (
            not username.isalnum()
        )
        if (invalid):
            raise PlantalyticsDataException(USER_INVALID)
        exists = cassy.check_username_exists(username)
        if (exists):
            raise PlantalyticsDataException(USER_TAKEN)
        message = (
            'Submitted username successfully validated.'
        )
        logger.info(message)
    except PlantalyticsException as e:
        raise e
    except Exception as e:
        raise e


def check_subscription_end_date(sub_end_date, current_date):
    """
    Validates submitted user subscription end date.
    """

    try:
        message = (
            'Validating submitted user subscription end date.'
        )
        logger.info(message)
        if sub_end_date != '':
            expected = datetime.datetime.strptime(sub_end_date, '%Y-%m-%d').strftime('%Y-%m-%d')
            date = sub_end_date.split('-')
            invalid = (
                sub_end_date != expected or
                len(date) != 3
            )
            if invalid is True:
                raise PlantalyticsDataException("Expected date format: YYYY-MM-DD")
            if time.strptime(sub_end_date, '%Y-%m-%d') < time.strptime(current_date, '%Y-%m-%d'):
                raise PlantalyticsDataException("Subcription end date has already passed.")
        message = (
            'Submitted user subscription end date successfully validated.'
        )
        logger.info(message)
    except PlantalyticsException as e:
        raise e
    except ValueError as e:
        raise PlantalyticsDataException("Expected date format: YYYY-MM-DD")
    except Exception as e:
        raise e


def check_user_parameters(user_info):
    """
    Checks submitted user data for parameter constraints.
    """

    email = user_info.get('email', '')
    sub_end_date = user_info.get('subenddate', '')
    vineyards = user_info.get('vineyards', '')
    current_date = datetime.date.today().strftime('%Y-%m-%d')
    new_user_id = user_info.get('userid', '')
    is_admin = user_info.get('admin', '')
    is_enable = user_info.get('enable', '')

    try:
        message = (
            'Validating submitted user parameters.'
        )
        logger.info(message)
        check_user_id(new_user_id)
        if email != '':
            if re.match(r"[^@]+@[^@]+\.[^@]+", email) is None:
                raise PlantalyticsDataException(EMAIL_INVALID)
        check_subscription_end_date(sub_end_date, current_date)
        if is_admin != '':
            if not isinstance(is_admin, bool):
                raise PlantalyticsDataException(DATA_INVALID)
        if is_enable != '':
            if not isinstance(is_enable, bool):
                raise PlantalyticsDataException(DATA_INVALID)
        if vineyards != '':
            for vineyard_id in vineyards:
                if int(vineyard_id) < 0:
                    raise PlantalyticsDataException(VINEYARD_BAD_ID)
        message = (
            'Submitted user parameters successfully validated.'
        )
        logger.info(message)
    except PlantalyticsException as e:
        raise e
    except ValueError as e:
        raise e
    except Exception as e:
        raise e


@csrf_exempt
def user_new(request):
    """
    Endpoint creates a new user with the requested user info.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    new_user_info = data.get('new_user_info', '')
    new_username = str(new_user_info.get('username', ''))
    password = new_user_info.get('password', '')
    email = new_user_info.get('email', '')
    is_admin = new_user_info.get('admin', '')
    is_enable = new_user_info.get('enable', '')
    sub_end_date = new_user_info.get('subenddate', '')
    user_id = new_user_info.get('userid', '')
    vineyards = new_user_info.get('vineyards', '')

    try:
        missing_values = (
            new_username == '' or
            password == '' or
            email == '' or
            is_admin == '' or
            is_enable == '' or
            auth_token == '' or
            sub_end_date == '' or
            user_id == '' or
            vineyards == ''
        )
        if (missing_values):
            raise PlantalyticsDataException(DATA_MISSING)
        if not verify_admin(auth_token):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            'Attemping to create new user: {}.'
        ).format(new_username)
        logger.info(message)
        check_username(new_username)
        check_user_parameters(new_user_info)
        cassy.create_new_user(new_user_info)
        message = (
            'Successfully created new user: {}.'
        ).format(new_username)
        logger.info(message)
        body = {
                'errors': {}
        }
        return HttpResponse(
            json.dumps(body),
            content_type='application/json'
        )
    except (PlantalyticsAuthException, PlantalyticsDataException) as e:
        message = (
            'Error attempting to create new user. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except PlantalyticsException as e:
        message = (
            'Error attempting to create new user. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except ValueError as e:
        message = (
            'Error attempting to create new user. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(USER_ID_INVALID, str(e))
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
    request_username = str(data.get('request_username', ''))
    sub_end_date = str(data.get('sub_end_date', ''))
    current_date = datetime.date.today().strftime('%Y-%m-%d')

    try:
        if not verify_admin(auth_token):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            'Attemping to update subscription for user: {}.'
        ).format(request_username)
        logger.info(message)
        check_subscription_end_date(sub_end_date, current_date)
        cassy.update_user_subscription(request_username, sub_end_date)
        message = (
            'Successfully updated subscruption for user: {}.'
        ).format(request_username)
        logger.info(message)
        body = {
                'errors': {}
        }
        return HttpResponse(
            json.dumps(body),
            content_type='application/json'
        )
    except PlantalyticsDataException as e:
        message = (
            'Error attempting to create new user. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(SUB_DATE_INVLAID, str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except PlantalyticsException as e:
        message = (
            'Error attempting to update user subscription. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except ValueError as e:
        message = (
            'Error attempting to update user subscription. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(SUB_DATE_INVLAID, str(e))
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
    edit_user_info = data.get('edit_user_info', '')
    username = str(edit_user_info.get('username', ''))

    try:
        if not verify_admin(auth_token):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            'Attemping to edit info for user: {}.'
        ).format(username)
        logger.info(message)
        check_user_parameters(edit_user_info)
        cassy.edit_user(edit_user_info)
        message = (
            'Successfully edited info for user: {}.'
        ).format(username)
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
    request_username = str(data.get('request_username', ''))

    try:
        if not verify_admin(auth_token):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            'Attemping to disable user: {}.'
        ).format(request_username)
        logger.info(message)
        cassy.disable_user(request_username)
        message = (
            'Successfully disabled user: {}.'
        ).format(request_username)
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
    vineyard_id = str(data.get('vineyard_id', ''))

    try:
        if not verify_admin(auth_token):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            'Retrieving vineyard info for vineyard id: {}.'
        ).format(vineyard_id)
        logger.info(message)
        response = cassy.get_vineyard_info(vineyard_id)
        message = (
            'Successfully retrieved vineyard info for vineyard id: {}.'
        ).format(vineyard_id)
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
    edit_vineyard_info = data.get('edit_vineyard_info', '')
    vineyard_id = str(edit_vineyard_info.get('vineyard_id', ''))

    try:
        if not verify_admin(auth_token):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            'Attemping to edit info for vineyard id: {}.'
        ).format(vineyard_id)
        logger.info(message)
        cassy.edit_vineyard(edit_vineyard_info)
        message = (
            'Successfully edited info for vineyard id: {}.'
        ).format(vineyard_id)
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


def check_vineyard_id(vineyard_id):
    """
    Validates submitted vineyard id by checking if it already exists.
    """

    message = (
        'Validating submitted vineyard id.'
    )
    logger.info(message)
    invalid = (
        vineyard_id == '' or
        int(vineyard_id) < 0 or
        cassy.check_vineyard_id_exists(int(vineyard_id))
    )
    if (invalid):
        raise PlantalyticsDataException(VINEYARD_ID_INVALID)
    message = (
        'Submitted vineyard id successfully validated.'
    )
    logger.info(message)


@csrf_exempt
def vineyard_new(request):
    """
    Endpoint creates a new vineyard with the requested user info.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    new_vineyard_info = data.get('new_vineyard_info', '')
    vineyard_id = str(new_vineyard_info.get('vineyard_id', ''))

    try:
        if not verify_admin(auth_token):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            'Attemping to create new vineyard with vineyard id: {}.'
        ).format(vineyard_id)
        logger.info(message)
        check_vineyard_id(vineyard_id)
        cassy.create_new_vineyard(new_vineyard_info)
        message = (
            'Successfully created new vineyard with vineyard id: {}.'
        ).format(vineyard_id)
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
    vineyard_id = str(data.get('vineyard_id', ''))

    try:
        if not verify_admin(auth_token):
            raise PlantalyticsAuthException(ADMIN_INVALID)

        message = (
            'Attemping to disable vineyard with vineyard id: {}.'
        ).format(vineyard_id)
        logger.info(message)
        response = cassy.disable_vineyard(vineyard_id)
        message = (
            'Successfully disabled vineyard with vineyard id: {}.'
        ).format(vineyard_id)
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
