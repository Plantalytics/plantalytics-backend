#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

import json

from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.http.response import HttpResponseRedirect


class MainTests(TestCase):
    """
    Executes all of the unit tests for plantalytics-backend.
    """

    def test_health_check_response(self):
        setup_test_environment()
        client = Client()
        response = client.get('/health_check')
        status = json.loads(response.content.decode('utf-8'))
        self.assertEqual(status['isAlive'], True)
        self.assertEqual(response.status_code, 200)
