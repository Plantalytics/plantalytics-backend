#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

from json import dumps

# Using constants to make it easier to rename codes
AUTH_NO_TOKEN = 'auth_error_no_token'
AUTH_UNKNOWN = 'auth_error_unknown'
AUTH_NOT_FOUND = 'auth_error_not_found'
CHANGE_ERROR_PASSWORD = 'reset_error_password'
CHANGE_EMAIL_UNKNOWN = 'change_email_unknown'
ENV_DATA_INVALID = 'env_data_invalid'
ENV_DATA_NOT_FOUND = 'env_data_not_found'
ENV_DATA_UNKNOWN = 'env_data_unknown'
EMAIL_RESET_ERROR = 'email_reset_error'
EMAIL_INVALID = 'email_bad_error'
HUB_KEY_INVALID = 'env_key_invalid'
LOGIN_ERROR = 'login_error'
LOGIN_UNKNOWN = 'login_unknown'
RESET_ERROR = 'reset_error'
RESET_ERROR_USERNAME = 'reset_error_username'
VINEYARD_NO_ID = 'vineyard_no_id'
VINEYARD_BAD_ID = 'vineyard_bad_id'
VINEYARD_ID_NOT_FOUND = 'vineyard_id_not_found'
VINEYARD_UNKNOWN = 'vineyard_unknown'
UNKNOWN = 'unknown'

responses = {
    AUTH_NO_TOKEN: 'Missing auth token in request.',
    AUTH_UNKNOWN: 'Unexpected error occurred during authorization.',
    AUTH_NOT_FOUND: 'Auth token not found.',
    CHANGE_ERROR_PASSWORD: 'Invalid new password.',
    CHANGE_EMAIL_UNKNOWN: 'Unknown error while attempting to change email',
    ENV_DATA_INVALID: (
        'Request for invalid environmental data. '
        'Must be one of leafwetness, humidity, or temperature.'
    ),
    ENV_DATA_NOT_FOUND: 'The request resulted in no environmental data.',
    ENV_DATA_UNKNOWN: (
        'An expected error occurred '
        'gathering the requested data.'
    ),
    EMAIL_RESET_ERROR: 'Email Error: Invalid username.',
    EMAIL_INVALID: 'Email Error: invalid or missing email',
    HUB_KEY_INVALID: 'Hub key invalid.',
    LOGIN_ERROR: 'Login Error: Invalid username or password.',
    LOGIN_UNKNOWN: 'An unexpected error occurred during login.',
    RESET_ERROR: 'An error occurred while resetting your password.',
    RESET_ERROR_USERNAME: (
        'An error occurred resetting the password. Bad username.'
    ),
    VINEYARD_NO_ID: 'A vineyard must have a valid ID.',
    VINEYARD_BAD_ID: 'A vineyard ID must be a positive integer.',
    VINEYARD_ID_NOT_FOUND: 'The vineyard ID was not found.',
    VINEYARD_UNKNOWN: (
        'An unexpected error occurred while fetching the vineyard ID.'
    ),
    UNKNOWN: 'An unknown error occurred.',
}


def custom_error(code, additional_message=None):
    """
    :param code: abbreviated text error code. ex 'auth_err'
    :param additional_message: Extra message appended to default message
    :return:
    """
    valid_code = code if code in responses else UNKNOWN
    message = responses[valid_code]
    message = (
        message + ' ' + additional_message if additional_message else message
    )
    result = {
        'errors':
        {
            valid_code: message
        }
    }
    return dumps(result)