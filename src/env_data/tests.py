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

from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from unittest.mock import patch


class MainTests(TestCase):
    """
    Executes all of the unit tests for the env_data endpoint.
    """

    def test_response_temperature_data(self):
        """
        Test env data endpoint when temperature data is requested.
        """
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'env_variable': 'temperature',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_env_data_invalid_method(self):
        """
        Tests the env_data endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/env_data')
        self.assertEqual(response.status_code, 405)

    @patch('cassy.get_env_data')
    def test_response_env_data_exception(self, env_data_mock):
        """
        Test env data endpoint when get_env_data throws Exception.
        """
        setup_test_environment()
        client = Client()
        env_data_mock.side_effect = Exception('Test exception')
        body = {
            'vineyard_id': '0',
            'env_variable': 'temperature',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('env_data_unknown' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_humidity_data(self):
        """
        Test env data endpoint when humidity data is requested.
        """
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'env_variable': 'humidity',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_leafwetness_data(self):
        """
        Test env data endpoint when leafwetness data is requested.
        """
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'env_variable': 'leafwetness',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_invalid_vineyard(self):
        """
        Test env data endpoint when an invalid vineyard id is supplied.
        """
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '-1',
            'env_variable': 'temperature',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_id_not_found' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_invalid_env_variable(self):
        """
        Test env data endpoint when an invalid env variable is supplied.
        """
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'env_variable': 'cheesiness',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('env_data_invalid' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_env_data_request_missing_vineyard(self):
        """
        Test env data endpoint when a vineyard id is missing.
        """
        setup_test_environment()
        client = Client()
        body = {
            'env_variable': 'temperature',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_no_id' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_env_data_request_missing_env_variable(self):
        """
        Test env data endpoint when an env variable is missing.
        """
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('env_data_invalid' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_invalid_env_data_request_non_integer_id(self):
        """
        Test env data endpoint when an invalid vineyard id type is supplied.
        """
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': 'asdf',
            'env_variable': 'temperature',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_bad_id' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_env_data_invalid_token(self):
        """
        Test env data endpoint when an invalid token is supplied.
        """
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'env_variable': 'temperature',
            'auth_token': 'chestercheetah',
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
