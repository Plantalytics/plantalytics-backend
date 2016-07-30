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

    def test_response_valid_login(self):
        setup_test_environment()
        client = Client()
        payload = {}
        payload['username'] = os.environ.get('LOGIN_USERNAME')
        payload['password'] = os.environ.get('LOGIN_PASSWORD')
        response = client.post(
            '/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_invalid_username(self):
        setup_test_environment()
        client = Client()
        payload = {}
        payload['username'] = 'mrawesome'
        payload['password'] = os.environ.get('LOGIN_PASSWORD')
        response = client.post(
            '/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('login_error' in error)
        self.assertEqual(response.status_code, 403)

    def test_response_username_missing(self):
        setup_test_environment()
        client = Client()
        payload = {}
        payload['password'] = os.environ.get('LOGIN_PASSWORD')
        response = client.post(
            '/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_response_invalid_password(self):
        setup_test_environment()
        client = Client()
        payload = {}
        payload['username'] = os.environ.get('LOGIN_USERNAME')
        payload['password'] = 'notcorrect'
        response = client.post(
            '/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('login_error' in error)
        self.assertEqual(response.status_code, 403)

    def test_response_password_missing(self):
        setup_test_environment()
        client = Client()
        payload = {}
        payload['username'] = os.environ.get('LOGIN_USERNAME')
        response = client.post(
            '/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('login_error' in error)
        self.assertEqual(response.status_code, 403)

    @patch('cassy.get_user_password')
    def test_login_get_user_password_exception(self, password_mock):
        '''
        Tests the login endpoint when get_user_password throws Exception
        Args:
            mock_requests:

        Returns:

        '''
        setup_test_environment()
        client = Client()
        password_mock.side_effect = Exception('Test exception')
        payload = {}
        payload['username'] = os.environ.get('LOGIN_USERNAME')
        payload['password'] = os.environ.get('LOGIN_PASSWORD')
        response = client.post(
            '/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('login_unknown' in error)
        self.assertEqual(response.status_code, 403)

    def test_get_auth_token(self):
        setup_test_environment()
        rows = cassy.get_user_auth_token(
            os.environ.get('LOGIN_USERNAME'),
            os.environ.get('LOGIN_PASSWORD')
        )
        self.assertEqual(rows != None, True)

    def test_response_store_auth_token(self):
        setup_test_environment()
        result = cassy.set_user_auth_token(
            os.environ.get('LOGIN_USERNAME'),
            os.environ.get('LOGIN_PASSWORD'),
            os.environ.get('LOGIN_SEC_TOKEN')
        )
        self.assertEqual(result, True)

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
        response = client.get(
            '/vineyard'
            + '?vineyard_id=0&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_unknown' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_vinemeta_invalid_vineyard(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/vineyard'
            + '?vineyard_id=101&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_id_not_found' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_vinemeta_vineyard_missing(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/vineyard'
            + '?securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_no_id' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_vinemeta_invalid_vineyard_non_integer(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/vineyard'
            + '?vineyard_id=abc&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_bad_id' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_vineyard_metadata_invalid_token(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/vineyard'
            + '?vineyard_id=0&'
            + 'securitytoken=ChesterCheetah'
        )
        self.assertEqual(response.status_code, 403)

    def test_response_temperature_data(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=0&'
            + 'env_variable=temperature&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
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
        response = client.get(
            '/env_data'
            + '?vineyard_id=0&'
            + 'env_variable=temperature&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('env_data_unknown' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_humidity_data(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=0&'
            + 'env_variable=humidity&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        self.assertEqual(response.status_code, 200)

    def test_response_leafwetness_data(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=0&'
            + 'env_variable=leafwetness&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        self.assertEqual(response.status_code, 200)

    def test_response_invalid_vineyard(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=101&'
            + 'env_variable=temperature&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_id_not_found' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_invalid_env_variable(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=0&'
            + 'env_variable=cheesiness&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('env_data_invalid' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_invalid_env_data_request(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=101&'
            + 'env_variable=cheesiness&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_id_not_found' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_invalid_env_data_request_missing_vineyard(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?env_variable=cheesiness&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_no_id' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_invalid_env_data_request_missing_env_variable(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=0&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('env_data_invalid' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_invalid_env_data_request_non_integer_id(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=asdf&'
            + 'env_variable=temperature&'
            + 'securitytoken='
            + os.environ.get('LOGIN_SEC_TOKEN')
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_bad_id' in error)
        self.assertEqual(response.status_code, 400)

    def test_response_env_data_invalid_token(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data'
            + '?vineyard_id=101&'
            + 'env_variable=cheesiness&'
            + 'securitytoken=ChesterCheetah'
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
