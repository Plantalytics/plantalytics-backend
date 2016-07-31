#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

# Create tests here
import os
import json

from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from unittest.mock import patch


class MainTests(TestCase):
    """
    Executes all of the unit tests for plantalytics-backend.
    Mocking change_user_password since we don't want to change a password on the DB in most cases in tests
    """

    @patch('cassy.change_user_password')
    def test_password_change(self, cassy_mock):
        """
         Tests the case where user is logged in, requests a new password
        """
        setup_test_environment()
        client = Client()
        username = os.environ.get('LOGIN_USERNAME')
        new_password = 'newpass'
        body = {
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
            'old': os.environ.get('LOGIN_PASSWORD'),
            'password': new_password
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        cassy_mock.assert_called_once_with(username, new_password)
        self.assertEqual(response.status_code, 200)

    @patch('cassy.change_user_password')
    def test_password_change_with_mail_token(self, cassy_mock):
        """
        Tests the case where a user logs in after having gotten a password reset email.
        """
        setup_test_environment()
        client = Client()
        username = os.environ.get('LOGIN_USERNAME')
        new_password = 'newpass'
        body = {
            'token': os.environ.get('LOGIN_SEC_TOKEN'),
            'username': username,
            'password': new_password
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        cassy_mock.assert_called_once_with(username, new_password)
        self.assertEqual(response.status_code, 200)

    @patch('cassy.change_user_password')
    @patch('cassy.verify_auth_token')
    def test_password_change_with_admin(self, cassy_auth, cassy_mock):
        """
        Tests the case where an admin resets someone's password.
        Mocking the admin authentication.
        """
        setup_test_environment()
        client = Client()
        cassy_auth.return_value = 'admin'
        username = 'mr.forgetful'
        new_password = 'newpass'
        auth_token = os.environ.get('LOGIN_SEC_TOKEN')
        body = {
            'auth_token': auth_token,
            'username': username,
            'password': new_password
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        cassy_mock.assert_called_once_with(username, new_password)
        cassy_auth.assert_called_once_with(auth_token)
        self.assertEqual(response.status_code, 200)

    def test_password_email_reset_mismatched_username(self):
        """
        Tests the unexpected case where a user uses an email reset, but the username doesn't match the one retrieved
        """
        setup_test_environment()
        client = Client()
        username = 'bad_username'
        new_password = 'newpass'
        body = {
            'token': os.environ.get('LOGIN_SEC_TOKEN'),
            'username': username,
            'password': new_password
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('login_error' in error)
        self.assertEqual(response.status_code, 403)

    @patch('cassy.verify_auth_token')
    def test_password_change_with_admin_empty_username(self, cassy_auth):
        """
        Tests the case where an admin resets someone's password but with an empty or missing username
        Mocking the admin authentication.
        """
        setup_test_environment()
        client = Client()
        cassy_auth.return_value = 'admin'
        new_password = 'newpass'
        auth_token = os.environ.get('LOGIN_SEC_TOKEN')
        body = {
            'auth_token': auth_token,
            'password': new_password
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('reset_error_username' in error)
        cassy_auth.assert_called_once_with(auth_token)
        self.assertEqual(response.status_code, 400)

    def test_password_change_incorrect_old_pass(self):
        """
         Tests the case where user is logged in, requests a new password but supplies incorrect old password
        """
        setup_test_environment()
        client = Client()
        new_password = 'newpass'
        body = {
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
            'old': 'badpass',
            'password': new_password
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('login_error' in error)
        self.assertEqual(response.status_code, 403)

    def test_password_change_using_get(self):
        """
         Tests the case where user is logged in, requests a new password but supplies incorrect old password
        """
        setup_test_environment()
        client = Client()
        response = client.get(
            '/password/change'
            + '?auth_token=' + os.environ.get('LOGIN_SEC_TOKEN')
            + '&old=badpass'
            + '&password=newpass'
        )
        self.assertEqual(response.status_code, 400)

    @patch('cassy.change_user_password')
    def test_password_change_with_unknown_exception(self, cassy_mock):
        """
        Tests the case where a user logs in after having gotten a password reset email.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Mock exception')
        username = os.environ.get('LOGIN_USERNAME')
        new_password = 'newpass'
        body = {
            'token': os.environ.get('LOGIN_SEC_TOKEN'),
            'username': username,
            'password': new_password
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        cassy_mock.assert_called_once_with(username, new_password)
        self.assertEqual(response.status_code, 500)
