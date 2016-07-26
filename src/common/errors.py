#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

from json import dumps

responses = {
    'auth_error_no_token': 'Missing auth token in request.',
    'auth_error_unknown': 'Unexpected error occurred during authorization.',
    'auth_error_not_found': 'Auth token not found.',
    'env_data_invalid': 'Request for invalid environmental data. Must be one of leafwetness, humidity, or temperature.',
    'env_data_not_found': 'The request resulted in no environmental data.',
    'env_data_unknown': 'An expected error occurred gathering the requested data.',
    'login_error': 'Login Error: Invalid username or password.',
    'login_unknown': 'An unexpected error occurred during login.',
    'vineyard_no_id': 'A vineyard must have a valid ID.',
    'vineyard_bad_id': 'A vineyard ID must be a positive integer.',
    'vineyard_id_not_found': 'The vineyard ID was not found.',
    'vineyard_unknown': 'An unexpected error occurred while fetching the vineyard ID.',
    'unknown': 'An unknown error occurred.'
}


def custom_error(code, additional_message=None):
    """
    :param code: abbreviated text error code. ex 'auth_err'
    :param additional_message: Extra message appended to default message
    :return:
    """
    valid_code = code if code in responses else 'unknown'
    message = responses[valid_code]
    message = message + ' ' + additional_message if additional_message else message
    result = {'errors':
        {
            valid_code: message
        }
    }
    return dumps(result)
