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

import cassy

def index(request):
    """
    Mock auth endpoint to return success if correct user/pass are passed in.
    """
    username = request.GET.get('username','')
    submitted_password = request.GET.get('password','')

    try:
        stored_password = cassy.get_user_password(username)
        if stored_password == submitted_password:
            return HttpResponse()
        else:
            return HttpResponseForbidden()
    except Exception as e:
        return HttpResponseForbidden()
