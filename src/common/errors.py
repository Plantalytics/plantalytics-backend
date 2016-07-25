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
    'auth_err': 'Authorization error: ',
    'login_err': 'Login Error: Invalid username or password',
    'vin_err': 'Vineyard error: ',
    'unknown': 'An unknown error occurred: '
}


def custom_error(code, additional_message=None):
    """
    :param code: abbreviated text error code. ex 'auth_err'
    :param additional_message: Extra message appended to default message
    :return:
    """
    valid_code = code if code in responses else 'unknown'
    message = responses[valid_code]
    message = message + additional_message if additional_message else message
    result = {'errors':
        {
            valid_code: message
        }
    }
    return dumps(result)
