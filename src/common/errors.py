#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

from json import dumps


def custom_error(code, message):
    """
    :param code: abbreviated text error code. ex 'auth_err'
    :param message: verbose error message
    :return:
    """
    result = {'errors':
        {
            code: message
        }
    }
    return dumps(result)
