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
import string
import random

from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from common.exceptions import *
from unittest.mock import patch

import cassy


class MainTests(TestCase):
    """
    Executes all of the unit tests for plantalytics-backend.
    Mocking change_user_password since we don't want to
    change a password on the DB in most cases in tests.
    """

    @patch('cassy.change_user_password')
    def test_password_change(self, cassy_mock):
        """
         Tests the case where user is logged in, requests a new password
        """
        setup_test_environment()
        client = Client()
        username = os.environ.get('LOGIN_USERNAME')
        old_password = os.environ.get('LOGIN_PASSWORD')
        new_password = 'newpass'
        body = {
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
            'old': os.environ.get('LOGIN_PASSWORD'),
            'password': new_password,
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        cassy_mock.assert_called_once_with(
            username,
            new_password,
            old_password
        )
        self.assertEqual(response.status_code, 200)

    def test_password_change_with_admin_and_dummy_user(self):
        """
        Tests the case where an admin resets someone's password.
        Generates random password for dummy user.
        """
        setup_test_environment()
        client = Client()
        username = 'welches'
        new_password = ''.join(
            random.choice(
                string.ascii_letters +
                string.digits
            )
            for _ in range(6)
        )
        auth_token = 'token'
        body = {
            'auth_token': auth_token,
            'username': username,
            'password': new_password,
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    @patch('cassy.change_user_password')
    def test_password_change_with_mail_token(self, cassy_mock):
        """
        Tests the case where a user logs in after
        receiving gotten a password reset email.
        """
        setup_test_environment()
        client = Client()
        username = os.environ.get('LOGIN_USERNAME')
        old_password = os.environ.get('LOGIN_PASSWORD')
        new_password = 'newpass'
        body = {
            'token': os.environ.get('LOGIN_SEC_TOKEN'),
            'username': username,
            'password': new_password,
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        cassy_mock.assert_called_once_with(
            username,
            new_password,
            old_password
        )
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
        cassy_auth.return_value = str(os.environ.get('ADMIN'))
        username = 'mr.forgetful'
        old_password = 'testme'
        new_password = 'newpass'
        auth_token = 'token'
        body = {
            'auth_token': auth_token,
            'username': username,
            'password': new_password,
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        cassy_mock.assert_called_once_with(
            username,
            new_password,
            old_password
        )
        cassy_auth.assert_called_once_with(auth_token)
        self.assertEqual(response.status_code, 200)

    def test_password_change_with_invalid_user(self):
        """
        Tests the case where an admin resets someone's password
        for a user that does not exist.
        """
        setup_test_environment()
        username = 'ChesterCheetah'
        old_password = 'TheCheesiest'
        new_password = 'NotGonnaDooooIt'
        try:
            rows = cassy.change_user_password(
                username,
                new_password,
                old_password
            )
        except PlantalyticsException as e:
            self.assertEqual('reset_error_username', str(e))

    def test_password_email_reset_mismatched_username(self):
        """
        Tests the unexpected case where a user uses an email reset,
        but the username doesn't match the one retrieved
        """
        setup_test_environment()
        client = Client()
        username = 'bad_username'
        new_password = 'newpass'
        body = {
            'token': os.environ.get('LOGIN_SEC_TOKEN'),
            'username': username,
            'password': new_password,
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
        Tests the case where an admin resets someone's password,
        but with an empty or missing username.
        Mocking the admin authentication.
        """
        setup_test_environment()
        client = Client()
        cassy_auth.return_value = str(os.environ.get('ADMIN'))
        new_password = 'newpass'
        auth_token = 'token'
        body = {
            'auth_token': auth_token,
            'password': new_password,
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
         Tests the case where user is logged in, requests a new password,
         but supplies incorrect old password.
        """
        setup_test_environment()
        client = Client()
        new_password = 'newpass'
        body = {
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
            'old': 'badpass',
            'password': new_password,
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('login_error' in error)
        self.assertEqual(response.status_code, 403)

    def test_password_change_using_invalid_method(self):
        """
         Tests attempting a password change with unsupported method.
        """
        setup_test_environment()
        client = Client()
        url = (
            '/password/change'
            '?auth_token={}&'
            'old=badpass&'
            'password=newpass'
        ).format(str(os.environ.get('LOGIN_SEC_TOKEN')))
        response = client.get(url)
        self.assertEqual(response.status_code, 405)

    @patch('cassy.change_user_password')
    def test_password_change_with_unknown_exception(self, cassy_mock):
        """
        Tests the case where a user logs in after
        receiving a password reset email.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Mock exception')
        username = os.environ.get('LOGIN_USERNAME')
        old_password = os.environ.get('LOGIN_PASSWORD')
        new_password = 'newpass'
        body = {
            'token': os.environ.get('LOGIN_SEC_TOKEN'),
            'username': username,
            'password': new_password,
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        cassy_mock.assert_called_once_with(
            username,
            new_password,
            old_password
        )
        self.assertEqual(response.status_code, 500)

    @patch('cassy.change_user_password')
    def test_password_change_same_old_and_new(self, cassy_mock):
        """
         Tests the case where user is logged in, requests a new password.
        """
        setup_test_environment()
        client = Client()
        username = os.environ.get('LOGIN_USERNAME')
        old_password = os.environ.get('LOGIN_PASSWORD')
        new_password = os.environ.get('LOGIN_PASSWORD')
        body = {
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
            'old': os.environ.get('LOGIN_PASSWORD'),
            'password': new_password,
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        cassy_mock.assert_not_called()
        self.assertTrue('reset_error_password' in error)
        self.assertEqual(response.status_code, 400)

    @patch('cassy.change_user_password')
    def test_mail_token_password_change_same_old_and_new(self, cassy_mock):
        """
        Tests the case where a user logs in after receiving
        a password reset email.
        """
        setup_test_environment()
        client = Client()
        username = os.environ.get('LOGIN_USERNAME')
        old_password = os.environ.get('LOGIN_PASSWORD')
        new_password = os.environ.get('LOGIN_PASSWORD')
        body = {
            'token': os.environ.get('LOGIN_SEC_TOKEN'),
            'username': username,
            'password': new_password,
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        cassy_mock.assert_not_called()
        self.assertTrue('reset_error_password' in error)
        self.assertEqual(response.status_code, 400)

    @patch('cassy.change_user_password')
    @patch('cassy.verify_auth_token')
    def test_admin_password_change_same_old_and_new(
        self,
        cassy_auth,
        cassy_mock
    ):
        """
        Tests the case where an admin resets someone's password.
        Mocking the admin authentication.
        """
        setup_test_environment()
        client = Client()
        cassy_auth.return_value = str(os.environ.get('ADMIN'))
        username = 'mr.forgetful'
        old_password = 'testme'
        new_password = 'testme'
        auth_token = 'token'
        body = {
            'auth_token': auth_token,
            'username': username,
            'password': new_password,
        }
        response = client.post(
            '/password/change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        cassy_mock.assert_not_called()
        cassy_auth.assert_called_once_with(auth_token)
        self.assertTrue('reset_error_password' in error)
        self.assertEqual(response.status_code, 400)

    @patch('cassy.get_user_email')
    def test_password_reset_invalid_username(self, cassy_mock):
        """
        Tests the password reset endpoint with invalid username.
        Uses a DB Mock.
        """
        setup_test_environment()
        client = Client()
        username = 'ChesterCheetah'
        body = {
            'username': username,
        }
        response = client.post(
            '/password/reset',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        cassy_mock.assert_called_once_with(username)
        self.assertTrue('login_error' in error)
        self.assertEqual(response.status_code, 403)

    def test_password_reset_valid_username(self):
        """
        Tests the password reset endpoint with an email generated.
        """
        setup_test_environment()
        client = Client()
        username = 'welches'
        body = {
            'username': username,
        }
        response = client.post(
            '/password/reset',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    @patch('cassy.get_user_email')
    def test_password_reset_unknown_exception(self, cassy_mock):
        """
        Tests the password reset endpoint when
        cassy.get_vineyard_coordinates throws Exception.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Test exception')
        username = 'welches'
        body = {
            'username': username,
        }
        response = client.post(
            '/password/reset',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('email_error' in error)
        self.assertEqual(response.status_code, 403)

    def test_password_reset_invalid_method(self):
        """
        Tests the password reset endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/password/reset')
        self.assertEqual(response.status_code, 405)

    def test_set_auth_token_with_no_token(self):
        """
        Tests the case where a user's auth token is being set and no
        token is supplied.
        """
        setup_test_environment()
        username = 'ChesterCheetah'
        password = 'TheCheesiest'
        auth_token = ''
        try:
            rows = cassy.set_user_auth_token(
               username,
               password,
               auth_token
            )
        except PlantalyticsException as e:
            self.assertEqual('auth_error_no_token', str(e))

    def test_get_auth_token_with_invalid_user(self):
        """
        Tests the case where a user's auth token is being retrieved and an
        invalid username is supplied.
        """
        setup_test_environment()
        username = 'ChesterCheetah'
        password = 'TheCheesiest'
        try:
            rows = cassy.get_user_auth_token(
                username,
                password
            )
        except PlantalyticsException as e:
            self.assertEqual('auth_error_not_found', str(e))

    def test_get_user_email_with_no_username(self):
        """
        Tests the case where a user's email is being retrieved and no
        username is supplied.
        """
        setup_test_environment()
        username = ''
        try:
            rows = cassy.get_user_email(username)
        except PlantalyticsException as e:
            self.assertEqual('email_error', str(e))

    def test_get_user_email_with_invalid_user(self):
        """
        Tests the case where a user's email is being retrieved and an
        invalid username is supplied.
        """
        setup_test_environment()
        username = 'ChesterCheetah'
        try:
            rows = cassy.get_user_email(username)
        except PlantalyticsException as e:
            self.assertEqual('email_error', str(e))
