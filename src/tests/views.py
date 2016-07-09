#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

import logging

from django.http import HttpResponse

logger = logging.getLogger('plantalytics_backend.tests')


def index(request):
    logger.info('Hello, Logging World!!')
    return HttpResponse(
                'Hello , Plantalytics World!! '
                + 'Welcome to the backend, '
                + 'where things ain\'t pretty, but they get stuff DONE!'
    )
