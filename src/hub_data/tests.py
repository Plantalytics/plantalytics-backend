#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

import os
import json
import time

from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from unittest.mock import patch

import cassy


class MainTests(TestCase):
    """
    Executes all of the unit tests for the hub_data endpoint.
    """

    def test_response_valid_hub_data(self):
        setup_test_environment()
        client = Client()

        payload = {}
        payload['key'] = os.environ.get('HUB_KEY')
        payload['vine_id'] = 0
        payload['hub_id'] = 0
        hub_data = []
        i = 0
        while i <= 2:
            data_point = {}
            data_point['node_id'] = i
            data_point['temperature'] = 12345.00
            data_point['humidity'] = 12345.00
            data_point['leafwetness'] = 12345.00
            data_point['data_sent'] = int(time.time()*1000)
            hub_data.append(data_point)
            i = i + 1
        payload['hub_data'] = hub_data
        payload['batch_sent'] = int(time.time()*1000)

        response = client.post(
            '/hub_data',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_invalid_hub_data(self):
        setup_test_environment()
        client = Client()

        payload = {}
        payload['key'] = os.environ.get('HUB_KEY')
        payload['vine_id'] = 0
        payload['hub_id'] = 0
        hub_data = []
        i = 0
        while i <= 2:
            data_point = {}
            data_point['node_id'] = i
            data_point['data_sent'] = int(time.time()*1000)
            hub_data.append(data_point)
            i = i + 1
        payload['hub_data'] = hub_data
        payload['batch_sent'] = int(time.time()*1000)

        response = client.post(
            '/hub_data',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_response_hub_data_invalid_key(self):
        setup_test_environment()
        client = Client()

        payload = {}
        payload['key'] = '12345'
        payload['vine_id'] = 0
        payload['hub_id'] = 0
        hub_data = []
        i = 0
        while i <= 2:
            data_point = {}
            data_point['node_id'] = i
            data_point['temperature'] = 12345.00
            data_point['humidity'] = 12345.00
            data_point['leafwetness'] = 12345.00
            data_point['data_sent'] = int(time.time()*1000)
            hub_data.append(data_point)
            i = i + 1
        payload['hub_data'] = hub_data
        payload['batch_sent'] = int(time.time()*1000)

        response = client.post(
            '/hub_data',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
