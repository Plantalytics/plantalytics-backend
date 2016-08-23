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
import os

import cassy
from django.views.decorators.csrf import csrf_exempt
from common.exceptions import *
from common.errors import *
from django.conf import settings
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseBadRequest,
    HttpResponseServerError,
    HttpResponseNotAllowed
)
from django.core.mail import send_mail
from django.utils.http import urlencode

logger = logging.getLogger('plantalytics_backend.login')


def reset_auth_token(username, new_password):
    """
    Changes the reset token after changing user's password via the
    forgot password link.
    """

    try:
        logger.info('Resetting user auth token.')
        new_auth_token = str(uuid.uuid4())
        cassy.set_user_auth_token(
            username,
            new_password,
            new_auth_token
        )
        logger.info('Successfully reset user auth token.')
    except PlantalyticsException as e:
        raise e
    except Exception as e:
        raise e


@csrf_exempt
def change(request):
    """
    Mock auth endpoint to return success with generated token
    if correct user/pass are passed in.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))

    auth_token = str(data.get('auth_token', ''))
    username = str(data.get('username', ''))
    new_password = str(data.get('password', ''))
    old_password = str(data.get('old', ''))
    reset_token = str(data.get('token', ''))

    logger.info('Request to change password.')
    try:
        # User forgot password and reset token is given via email link
        if reset_token:
            logger.info('Attempting password reset using reset token.')
            reset_name = cassy.verify_auth_token(reset_token)
            stored_password = cassy.get_user_password(reset_name)

            if reset_name != username:
                message = (
                    'Username associated with reset token (\'{}\') '
                    'does not match supplied username (\'{}\').'
                ).format(reset_name, username)
                logger.warn(message)
                raise PlantalyticsLoginException(LOGIN_ERROR)
            if new_password == stored_password:
                logger.warn('Invalid new password.')
                raise PlantalyticsPasswordException(CHANGE_ERROR_PASSWORD)

            cassy.change_user_password(
                username,
                new_password,
                stored_password
            )
            message = (
                'Password for \'{}\' successfully changed.'
            ).format(username)
            logger.info(message)
            reset_auth_token(
                username,
                new_password
            )
        # Else, password being reset by admin or logged-in user
        else:
            logger.info('Attempting password reset using auth token.')
            verified_admin = cassy.verify_authenticated_admin(auth_token)
            # if the auth token is associated with the admin user,
            if verified_admin is True:
                if username:
                    stored_password = cassy.get_user_password(username)
                    if new_password == stored_password:
                        logger.warn('Invalid new password.')
                        raise PlantalyticsPasswordException(
                            CHANGE_ERROR_PASSWORD
                        )
                    message = (
                        'Admin resetting password for {}'
                    ).format(username)
                    logger.info(message)
                    cassy.change_user_password(
                        username,
                        new_password,
                        stored_password
                    )
                else:
                    logger.warn('Invalid username. Username cannot be empty.')
                    raise PlantalyticsException(RESET_ERROR_USERNAME)
            else:
                verified_name = cassy.verify_auth_token(auth_token)
                message = (
                    'User \'{}\' attempting to reset password.'
                ).format(verified_name)
                logger.info(message)

                stored_password = cassy.get_user_password(verified_name)
                if new_password == stored_password:
                    logger.warn('Invalid new password.')
                    raise PlantalyticsPasswordException(CHANGE_ERROR_PASSWORD)
                if stored_password != old_password:
                    logger.warn(
                        'Old password does not match supplied password.'
                    )
                    raise PlantalyticsLoginException(LOGIN_ERROR)
                cassy.change_user_password(
                    verified_name,
                    new_password,
                    stored_password
                )

    except (PlantalyticsAuthException, PlantalyticsLoginException) as e:
        message = (
            'Error attempting to change password. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except PlantalyticsException as e:
        message = (
            'Error attempting to change password. Error code: {}'
        ).format(str(e))
        logger.warn(message)
        error = custom_error(str(e))
        return HttpResponseBadRequest(error, content_type='application/json')
    except Exception as e:
        logger.exception(
            'Unknown error occurred while attempting to reset password:'
        )
        error = custom_error(UNKNOWN, str(e))
        return HttpResponseServerError(error, content_type='application/json')
    body = {'errors': {}}
    return HttpResponse(json.dumps(body), content_type='application/json')


@csrf_exempt
def reset(request):
    """
    Endpoint to email a password reset token to the requested user.
    """

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    data = json.loads(request.body.decode('utf-8'))
    username = str(data.get('username', ''))

    try:
        email = {
            'email': cassy.get_user_email(username),
        }
        reset_token = {
            'reset_token': str(uuid.uuid4()),
        }
        url_parameters = {
            "id": reset_token['reset_token'],
            "username": username,
        }
        reset_url = (
            str(os.environ.get('RESET_URL')) +
            urlencode(url_parameters)
        )

        password = cassy.get_user_password(username)
        cassy.set_user_auth_token(
            username,
            password,
            reset_token['reset_token']
        )
        message = (
            'Emailing reset token for user \'{}\'.'
        ).format(username)
        logger.info(message)

        send_mail(
            'Plantalytics Password Reset',
            reset_url,
            settings.EMAIL_HOST_USER,
            [email['email']],
            fail_silently=False,
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
            'Error occurred while fetching email for user \'{}\'. {}'
        ).format(username, str(e))
        logger.exception(message)
        error = custom_error(EMAIL_RESET_ERROR, str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    body = {'errors': {}}
    return HttpResponse(json.dumps(body), content_type='application/json')
