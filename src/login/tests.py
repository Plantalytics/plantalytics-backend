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
    Executes all of the unit tests for the login endpoint.
    """

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
        retrieved = True
        if rows is None:
            retrieved = False
        self.assertEqual(retrieved, True)

    def test_response_store_auth_token(self):
        setup_test_environment()
        result = cassy.set_user_auth_token(
            os.environ.get('LOGIN_USERNAME'),
            os.environ.get('LOGIN_PASSWORD'),
            os.environ.get('LOGIN_SEC_TOKEN')
        )
        self.assertEqual(result, True)
