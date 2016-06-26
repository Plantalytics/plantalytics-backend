#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

from django.http import HttpResponse


def index(request):   
    return HttpResponse('Hello , Plantalytics World!! '
                        + 'Welcome to the backend, '
                        + 'where things ain\'t pretty, but they get stuff DONE!')
