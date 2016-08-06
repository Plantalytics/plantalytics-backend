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

from common.exceptions import *
from django.test import TestCase, Client
from django.test.utils import setup_test_environment


class MainTests(TestCase):
    """
    Executes all of the unit tests for the hub_data endpoint.
    """

    def test_response_valid_hub_data(self):
        """
        Tests case when hub submits data with valid data.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'key': str(os.environ.get('HUB_KEY')),
            'vine_id': 0,
            'hub_id': 0,
        }
        hub_data = []
        num_of_nodes = 0
        while num_of_nodes <= 2:
            data_point = {
                'node_id': num_of_nodes,
                'temperature': 12345.00,
                'humidity': 12345.00,
                'leafwetness': 12345.00,
                'data_sent': int(time.time()*1000),
            }
            hub_data.append(data_point)
            num_of_nodes += 1
        payload['hub_data'] = hub_data
        payload['batch_sent'] = int(time.time()*1000)
        response = client.post(
            '/hub_data',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_missing_hub_data(self):
        """
        Tests case when hub submits data with missing data.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'key': str(os.environ.get('HUB_KEY')),
            'vine_id': 0,
            'hub_id': 0,
        }
        hub_data = []
        num_of_nodes = 0
        while num_of_nodes <= 2:
            data_point = {
                'node_id': num_of_nodes,
                'data_sent': int(time.time()*1000),
            }
            hub_data.append(data_point)
            num_of_nodes += 1
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
        payload = {
            'key': '12345',
            'vine_id': 0,
            'hub_id': 0,
        }
        hub_data = []
        num_of_nodes = 0
        while num_of_nodes <= 2:
            data_point = {
                'node_id': num_of_nodes,
                'temperature': 12345.00,
                'humidity': 12345.00,
                'leafwetness': 12345.00,
                'data_sent': int(time.time()*1000),
            }
            hub_data.append(data_point)
            num_of_nodes += 1
        payload['hub_data'] = hub_data
        payload['batch_sent'] = int(time.time()*1000)
        response = client.post(
            '/hub_data',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('env_key_invalid' in error)
        self.assertEqual(response.status_code, 403)
