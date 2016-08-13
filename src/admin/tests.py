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

from common.exceptions import *
from django.test import TestCase, Client
from django.test.utils import setup_test_environment


class MainTests(TestCase):
    """
    Executes all of the unit tests for the admin endpoints.
    """

    def test_user_info(self):
        """
        Tests a valid request for user info.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'admin_username': os.environ.get('ADMIN_USER'),
            'request_username': os.environ.get('LOGIN_USERNAME'),
        }
        response = client.post(
            '/admin/user',
            data=json.dumps(payload),
            content_type='application/json'
        )
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(
            content.get('email', ''),
            os.environ.get('RESET_EMAIL')
        )
        self.assertEqual(response.status_code, 200)

    def test_user_info_invalid_method(self):
        """
        Tests the user info endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/admin/user')
        self.assertEqual(response.status_code, 405)

    def test_user_update_sub_end_date(self):
        """
        Tests a valid request to update a user subscription date.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'admin_username': os.environ.get('ADMIN_USER'),
            'request_username': os.environ.get('LOGIN_USERNAME'),
            'sub_end_date': '2100-01-01',
        }
        response = client.post(
            '/admin/user/subscription',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_user_update_sub_end_date_invalid_method(self):
        """
        Tests the update user subscription end date endpoint
        with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/admin/user/subscription')
        self.assertEqual(response.status_code, 405)

    def test_new_user(self):
        """
        Tests a valid request to create a new user.
        """
        print(">>>>>TEST NEW USER!!!")
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'admin_username': os.environ.get('ADMIN_USER'),
            'new_user_info': {
                'username': os.environ.get('LOGIN_USERNAME'),
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'securitytoken': os.environ.get('LOGIN_SEC_TOKEN'),
                'subenddate': os.environ.get('LOGIN_SUB_END_DATE'),
                'userid': os.environ.get('LOGIN_USER_ID'),
                'vineyards': [int(os.environ.get('LOGIN_USER_ID'))],
            },
        }
        response = client.post(
            '/admin/user/new',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_new_user_invalid_method(self):
        """
        Tests the create new user endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/admin/user/new')
        self.assertEqual(response.status_code, 405)

    def test_disable_user(self):
        """
        Tests a valid request to disable a user.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'admin_username': os.environ.get('ADMIN_USER'),
            'request_username': os.environ.get('LOGIN_USERNAME'),
        }
        response = client.post(
            '/admin/user/disable',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_disable_user_invalid_method(self):
        """
        Tests the disable user endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/admin/user/disable')
        self.assertEqual(response.status_code, 405)
