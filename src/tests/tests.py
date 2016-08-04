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
    Executes all of the unit tests for plantalytics-backend.
    """

    def test_http_response(self):
        setup_test_environment()
        client = Client()
        response = client.get('/tests/')
        self.assertEqual(response.status_code, 200)

    def test_response_vineyard_metadata(self):
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
        }
        response = client.post(
            '/vineyard',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    @patch('cassy.get_vineyard_coordinates')
    def test_response_vineyard_metadata_exception(self, vineyard_mock):
        '''
        Tests vineyard endpoint when cassy.get_vineyard_coordinates throws Exception
        Args:
            vineyard_mock:

        Returns:

        '''
        setup_test_environment()
        client = Client()
        vineyard_mock.side_effect =Exception('Test exception')
        body = {
            'vineyard_id': '0',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
        }
        response = client.post(
            '/vineyard',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_unknown' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_vinemeta_invalid_vineyard(self):
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '-1',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
        }
        response = client.post(
            '/vineyard',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_id_not_found' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_vinemeta_vineyard_missing(self):
        setup_test_environment()
        client = Client()
        body = {
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
        }
        response = client.post(
            '/vineyard',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_no_id' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_vinemeta_invalid_vineyard_non_integer(self):
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': 'abc',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
        }
        response = client.post(
            '/vineyard',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_bad_id' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_vineyard_metadata_invalid_token(self):
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'auth_token': 'chestercheetah'
        }
        response = client.post(
            '/vineyard',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_response_temperature_data(self):
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'env_variable': 'temperature',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    @patch('cassy.get_env_data')
    def test_response_env_data_exception(self, env_data_mock):
        '''
        Test env_data endpoint when get_env_data throws Exception
        Args:
            env_data_mock:

        Returns:

        '''
        setup_test_environment()
        client = Client()
        env_data_mock.side_effect = Exception('Test exception')
        body = {
            'vineyard_id': '0',
            'env_variable': 'temperature',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
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
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'env_variable': 'humidity',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_leafwetness_data(self):
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'env_variable': 'leafwetness',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_invalid_vineyard(self):
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '-1',
            'env_variable': 'temperature',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
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
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'env_variable': 'cheesiness',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('env_data_invalid' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_invalid_env_data_request_missing_vineyard(self):
        setup_test_environment()
        client = Client()
        body = {
            'env_variable': 'temperature',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_no_id' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_invalid_env_data_request_missing_env_variable(self):
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
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
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': 'asdf',
            'env_variable': 'temperature',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN')
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
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'env_variable': 'temperature',
            'auth_token': 'chestercheetah'
        }
        response = client.post(
            '/env_data',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

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
