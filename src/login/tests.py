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

import cassy


class MainTests(TestCase):
    """
    Executes all of the unit tests for the login endpoint.
    """

    def test_response_valid_login(self):
        """
         Tests the case where user logs in with
         a valid username and password.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'username': str(os.environ.get('LOGIN_USERNAME')),
            'password': str(os.environ.get('LOGIN_PASSWORD')),
        }
        response = client.post(
            '/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_invalid_username(self):
        """
         Tests the case where user logs in with an invalid username.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'username': 'mrawesome',
            'password': str(os.environ.get('LOGIN_PASSWORD')),
        }
        response = client.post(
            '/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('login_error' in error)
        self.assertEqual(response.status_code, 403)

    def test_response_username_missing(self):
        """
         Tests the case where user logs in without a username.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'password': str(os.environ.get('LOGIN_PASSWORD')),
        }
        response = client.post(
            '/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_response_invalid_password(self):
        """
         Tests the case where user logs in with a valid username
         and an invalid password.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'username': str(os.environ.get('LOGIN_USERNAME')),
            'password': 'notcorrect',
        }
        response = client.post(
            '/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('login_error' in error)
        self.assertEqual(response.status_code, 403)

    def test_response_password_missing(self):
        """
         Tests the case where user logs in with a missing password.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'username': str(os.environ.get('LOGIN_USERNAME')),
        }
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
        """
        Tests the login endpoint when get_user_password throws Exception
        """
        setup_test_environment()
        client = Client()
        password_mock.side_effect = Exception('Test exception')
        payload = {
            'username': str(os.environ.get('LOGIN_USERNAME')),
            'password': str(os.environ.get('LOGIN_PASSWORD')),
        }
        response = client.post(
            '/login',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('login_unknown' in error)
        self.assertEqual(response.status_code, 403)

    def test_get_auth_token(self):
        """
        Tests the retrieving an auth token from the database.
        """
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
        """
        Tests the storing an auth token in the database.
        """
        setup_test_environment()
        result = cassy.set_user_auth_token(
            os.environ.get('LOGIN_USERNAME'),
            os.environ.get('LOGIN_PASSWORD'),
            os.environ.get('LOGIN_SEC_TOKEN')
        )
        self.assertEqual(result, True)
