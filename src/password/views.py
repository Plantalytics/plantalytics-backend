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

import cassy
from django.views.decorators.csrf import csrf_exempt
from common.exceptions import *
from common.errors import *
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseServerError

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

    auth_token = data.get('auth_token', '')
    username = data.get('username', '')
    new_password = data.get('password', '')
    old_password = data.get('old', '')
    reset_token = data.get('token', '')

    logger.info('Request to change password.')
    try:
        # User forgot password and reset token is given via email link
        if reset_token:
            logger.info('Attempting password reset using reset_token.')
            reset_name = cassy.verify_auth_token(reset_token)
            if reset_name != username:
                logger.warn(
                    "Username associated with reset token (\'{}\') ".format(reset_name)
                    + "does not match supplied username (\'{}\').".format(username)
                )
                raise PlantalyticsLoginException(LOGIN_ERROR)

            cassy.change_user_password(username, new_password)
            logger.info('Password for \'{}\' successfully changed.'.format(username))
        # Else, password being reset by admin or logged-in user
        else:
            logger.info('Attempting password reset using auth_token.')
            verified_name = cassy.verify_auth_token(auth_token)

            # if the auth token is associated with the admin user,
            if verified_name == 'admin':
                if username:
                    logger.info('Admin resetting password for {}'.format(username))
                    cassy.change_user_password(username, new_password)
                else:
                    logger.warn('Invalid username. Username cannot be empty.')
                    raise PlantalyticsException(RESET_ERROR_USERNAME)
            else:
                logger.info('User \'{}\' attempting to reset password.'.format(verified_name))
                stored_password = cassy.get_user_password(verified_name)
                if stored_password != old_password:
                    logger.warn('Old password does not match supplied password.')
                    raise PlantalyticsLoginException(LOGIN_ERROR)

                cassy.change_user_password(verified_name, new_password)

    except (PlantalyticsAuthException, PlantalyticsLoginException) as e:
        logger.warn(
            'Error attempting to change password. Error code: {}'
            .format(str(e))
        )
        error = custom_error(str(e))
        return HttpResponseForbidden(error, content_type='application/json')
    except PlantalyticsException as e:
        logger.warn(
            'Error attempting to change password. Error code: {}'
            .format(str(e))
        )
        error = custom_error(str(e))
        return HttpResponseBadRequest(error, content_type='application/json')
    except Exception as e:
        logger.exception(
            'Unknown error occurred while attempting to reset password:'
        )
        error = custom_error(UNKNOWN, str(e))
        return HttpResponseServerError(error, content_type='application/json')

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
