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
    x = 1
    while x < 10:
        x = x + 1
    y = 2
    while y < 20:
        y = y + 2
    z = 3
    while z< 30:
        z = z + 3    
    return HttpResponse('Hello , Plantalytics World!! '
                        + 'Welcome to the backend, '
                        + 'where things ain\'t pretty, but they get stuff DONE!')
