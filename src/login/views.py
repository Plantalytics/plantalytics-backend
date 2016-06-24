#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#
import os

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden

def index(request, username, password):
    """
    Mock auth endpoint to return success if correct user/pass are passed in.
    """

    if (username == os.environ.get('LOGIN_USERNAME') and
            password == os.environ.get('LOGIN_PASSWORD')):
        return HttpResponse()
    else:
        return HttpResponseForbidden()
