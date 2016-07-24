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

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest

import cassy

logger = logging.getLogger('plantalytics_backend.hub_data')


@csrf_exempt
def index(request):
    """
    Receive data from hub to insert into database.
    """

    data = json.loads(request.body.decode("utf-8"))

    try:
        logger.info('Inserting hub data.')
        cassy.post_env_data(data)
        logger.info('Successfully inserted hub data.')
        return HttpResponse()
    except Exception as e:
        logger.exception('Error occurred while inserting hub data.'
                         + str(e)
        )
        return HttpResponseBadRequest()