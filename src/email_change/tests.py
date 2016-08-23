#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

import json
import cassy

from common.exceptions import *
from common.errors import *
from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from unittest.mock import patch


class MainTests(TestCase):
    """
    Executes all of the unit tests for the env_data endpoint.
    """
    @patch('django.core.mail.send_mail')
    def test_email_change(self, send_mail_mock):
        """
        Test env data endpoint when temperature data is requested.
        """
        username = "username"
        old_email = cassy.get_user_email(username)
        setup_test_environment()
        client = Client()
        body = {
            "auth_token": "securitytoken",
            "new_email": "plant.alytics@gmail.com"
        }
        response = client.post(
            '/email_change',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # Reset back to old email
        body = {
            "auth_token": "securitytoken",
            "new_email": old_email
        }
        response = client.post(
            '/email_change',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_missing_token(self):
        """
        Test with missing auth token
        """
        setup_test_environment()
        client = Client()

        body = {
            "new_email": "plantalytics@gmail.com"
        }
        response = client.post(
            '/email_change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        for key in error:
            self.assertEqual('auth_error_no_token', key)
        self.assertEqual(response.status_code, 400)

    def test_empty_token(self):
        """
        Test with empty auth token
        """
        setup_test_environment()
        client = Client()

        body = {
            "new_email": "plant.alytics@gmail.com",
            "auth_token": ""
        }
        response = client.post(
            '/email_change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        for key in error:
            self.assertEqual('auth_error_no_token', key)
        self.assertEqual(response.status_code, 400)

    def test_bad_auth_token(self):
        """
        Test with empty auth token
        """
        setup_test_environment()
        client = Client()

        body = {
            "new_email": "plant.alytics@gmail.com",
            "auth_token": "badtoken"
        }
        response = client.post(
            '/email_change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        for key in error:
            self.assertEqual('auth_error_not_found', key)
        self.assertEqual(response.status_code, 403)

    def test_missing_email(self):
        """
        Test with empty auth token
        """
        setup_test_environment()
        client = Client()

        body = {
            "auth_token": "securitytoken"
        }
        response = client.post(
            '/email_change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        for key in error:
            self.assertEqual('email_bad_error', key)
        self.assertEqual(response.status_code, 400)

    def test_bad_email(self):
        """
        Test with empty auth token
        """
        setup_test_environment()
        client = Client()

        body = {
            "new_email": "plantalyticsatgmail.com",
            "auth_token": "securitytoken"
        }
        response = client.post(
            '/email_change',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        for key in error:
            self.assertEqual('email_bad_error', key)
        self.assertEqual(response.status_code, 400)

    @patch("cassy.change_user_email")
    def test_email_change_with_plantalytics_exception(self, change_email_mock):
        """
        Test with a Plantalytics exception
        """
        change_email_mock.side_effect = (
            PlantalyticsException(CHANGE_EMAIL_UNKNOWN)
        )
        setup_test_environment()
        client = Client()

        body = {
            "new_email": "plantalytics@gmail.com",
            "auth_token": "securitytoken"
        }
        response = client.post(
            '/email_change',
            data=json.dumps(body),
            content_type='application/json'
        )
        #
        error = json.loads(response.content.decode('utf-8'))['errors']
        for key in error:
            self.assertEqual('change_email_unknown', key)
        self.assertEqual(response.status_code, 400)

    @patch("cassy.change_user_email")
    def test_email_change_with_unknown_exception(self, change_user_email_mock):
        """
        Test with a Plantalytics exception
        """
        change_user_email_mock.side_effect = Exception("Mock exception")
        setup_test_environment()
        client = Client()

        body = {
            "new_email": "plantalytics@gmail.com",
            "auth_token": "securitytoken"
        }
        response = client.post(
            '/email_change',
            data=json.dumps(body),
            content_type='application/json'
        )
        #
        error = json.loads(response.content.decode('utf-8'))['errors']
        for key in error:
            self.assertEqual('change_email_unknown', key)
        self.assertEqual(response.status_code, 500)

    def test_email_change_invalid_method(self):
        """
        Tests the email change endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/email_change')
        self.assertEqual(response.status_code, 405)
