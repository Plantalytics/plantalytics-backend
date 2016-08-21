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
import datetime
import time

from common.exceptions import PlantalyticsException
from common.errors import *
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden

import cassy

logger = logging.getLogger('plantalytics_backend.login')


def check_user_is_enabled(username):
    """
    Checks that the user account is enabled.
    """

    try:
        message = (
            'Verifying account for user \'{}\' is enabled.'
        ).format(username)
        logger.info(message)

        is_enabled = cassy.verify_user_account(username)
        if not is_enabled:
            return False
        return True

        message = (
            'Successfully verified account for user \'{}\'.'
        ).format(username)
        logger.info(message)
    except PlantalyticsException as e:
        raise e
    except Exception as e:
        raise e


def check_user_subscription_end_date(username):
    """
    Checks that the user account subscription date has not expired.
    """

    try:
        message = (
            'Verifying subscription for user \'{}\' has not expired.'
        ).format(username)
        logger.info(message)

        current_date = datetime.date.today().strftime('%Y-%m-%d')
        sub_end_date = cassy.get_user_subscription(username)
        if time.strptime(sub_end_date, '%Y-%m-%d') < time.strptime(current_date, '%Y-%m-%d'):
            return True
        return False

        message = (
            'Successfully verified subscription for user \'{}\'.'
        ).format(username)
        logger.info(message)
    except PlantalyticsException as e:
        raise e
    except Exception as e:
        raise e


def check_user_exists(username):
    """
    Checks that the user exists in the database
    """

    try:
        message = (
            'Verifying user \'{}\' exists.'
        ).format(username)
        logger.info(message)

        exists = cassy.check_username_exists(username)
        if not exists:
            return False
        return True

        message = (
            'Successfully verified user \'{}\' exists.'
        ).format(username)
        logger.info(message)
    except PlantalyticsException as e:
        raise e
    except Exception as e:
        raise e


@csrf_exempt
def index(request):
    """
    Mock auth endpoint to return success with generated token
    if valid username and password pair is passed in.
    """

    data = json.loads(request.body.decode("utf-8"))
    username = str(data.get('username', ''))
    submitted_password = str(data.get('password', ''))

    try:
        if username == '':
            raise PlantalyticsException(LOGIN_ERROR)
        exists = check_user_exists(username)
        if not exists:
            raise PlantalyticsException(LOGIN_ERROR)
        is_enabled = check_user_is_enabled(username)
        if not is_enabled:
            raise PlantalyticsAuthException(AUTH_DISABLED)
        is_expired = check_user_subscription_end_date(username)
        if is_expired:
            raise PlantalyticsAuthException(AUTH_EXPIRED)
        # Get stored password from database, and verify with password arg
        message = (
            'Fetching password for user \'{}\'.'
        ).format(username)
        logger.info(message)

        stored_password = cassy.get_user_password(username)

        message = (
            'Successfully fetched password for user \'{}\'.'
        ).format(username)
        logger.info(message)

        if stored_password == submitted_password:
            # Generate token and put into JSON object
            response = {
                'auth_token': str(uuid.uuid4()),
            }
            # Return response with token object
            message = (
                'Storing auth token for user \'{}\'.'
            ).format(username)
            logger.info(message)

            cassy.set_user_auth_token(
                username,
                submitted_password,
                response['auth_token']
            )
            # Add in vineyard ids
            response['authorized_vineyards'] = cassy.get_authorized_vineyards(
                username
            )
            message = (
                'Successfully logged in user \'{}\'.'
            ).format(username)
            logger.info(message)
            return HttpResponse(
                json.dumps(response),
                content_type='application/json'
            )
        else:
            message = (
                'Incorrect password supplied for user \'{}\'.'
            ).format(username)
            logger.warning(message)
            error = custom_error(LOGIN_ERROR)
            return HttpResponseForbidden(
                error,
                content_type='application/json'
            )
    # Invalid username -- expected exception
    except PlantalyticsException as e:
        message = (
            'Unknown username \'{}\'.'
        ).format(username)
        logger.warning(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    # Unexpected exception
    except Exception as e:
        message = (
            'Error occurred while fetching password for user \'{}\'. {}'
        ).format(username, str(e))
        logger.exception(message)
        error = custom_error(LOGIN_UNKNOWN, str(e))
        return HttpResponseForbidden(error, content_type='application/json')
