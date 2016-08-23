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

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger('plantalytics_backend.health_check')


@csrf_exempt
def index(request):
    logger.info('It\'s Alive!!')
    response = {
        'isAlive': True,
    }
    return HttpResponse(json.dumps(response), content_type='application/json')
