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
from django.http.response import HttpResponseRedirect


class MainTests(TestCase):
    """
    Executes all of the unit tests for plantalytics-backend.
    """

    def test_http_response(self):
        setup_test_environment()
        client = Client()
        response = client.get('/tests/')
        self.assertEqual(response.status_code, 200)

    def test_response_valid_login(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/login?username='
            + os.environ.get('LOGIN_USERNAME')
            + '&password='
            + os.environ.get('LOGIN_PASSWORD')
        )
        self.assertEqual(response.status_code, 200)

    def test_response_invalid_username(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/login?username=mrawesome'
            + '&password='
            + os.environ.get('LOGIN_PASSWORD')
        )
        self.assertEqual(response.status_code, 403)

    def test_response_invalid_password(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/login?username='
            + os.environ.get('LOGIN_USERNAME')
            + '&password=notcorrect'
        )
        self.assertEqual(response.status_code, 403)

    def test_response_valid_auth_token(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/validate?username='
            + os.environ.get('LOGIN_USERNAME')
            + '&password='
            + os.environ.get('LOGIN_PASSWORD')
        )
        self.assertEqual(response.status_code, 200)

    def test_response_store_auth_token(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/store_token?username='
            + os.environ.get('LOGIN_USERNAME')
            + '&password='
            + os.environ.get('LOGIN_PASSWORD')
            + '&securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        self.assertEqual(response.status_code, 200)

    def test_response_valid_hub_data(self):
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
        self.assertEqual(response.status_code, 200)

    def test_response_invalid_hub_data(self):
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

    def test_response_vineyard_metadata(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/vineyard'
            + '?vineyard_id=0&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        self.assertEqual(response.status_code, 200)

    def test_response_vinemeta_invlaid_vineyard(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/vineyard'
            + '?vineyard_id=101&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        self.assertEqual(response.status_code, 400)

    def test_response_temperature_data(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=0&'
            + 'env_variable=temperature'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_humidity_data(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=0&'
            + 'env_variable=humidity'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_leafwetness_data(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=0&'
            + 'env_variable=leafwetness'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_invlaid_vineyard(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=101&'
            + 'env_variable=temperature'
        )
        self.assertEqual(response.status_code, 400)

    def test_response_invlaid_env_variable(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=0&'
            + 'env_variable=cheesiness'
        )
        self.assertEqual(response.status_code, 400)

    def test_response_invlaid_env_data_request(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=101&'
            + 'env_variable=cheesiness'
        )
        self.assertEqual(response.status_code, 400)

    def test_admin_redirect(self):
        setup_test_environment()
        client = Client()
        response = client.get('/admin/')
        expected_redirect_url = '/admin/login/?next=/admin/'
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, expected_redirect_url)

    def test_admin(self):
        setup_test_environment()
        client = Client()
        response = client.get('/admin/login/?next=/admin/')
        self.assertEqual(response.status_code, 200)
