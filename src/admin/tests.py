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
from unittest.mock import patch


class MainTests(TestCase):
    """
    Executes all of the unit tests for the admin endpoints.
    """

# /admin/user - valid request tests

    def test_user_info(self):
        """
        Tests a valid request for user info.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
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

# /admin/user - invalid request tests

    def test_user_info_invalid_username(self):
        """
        Tests a request for user info with an invalid username.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'request_username': 'thisGuyAintInThere',
        }
        response = client.post(
            '/admin/user',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('username_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_user_info_invalid_admin(self):
        """
        Tests a request for user info with an invalid admin credentials.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': 'thisWontGetYouFar',
            'request_username': os.environ.get('LOGIN_USERNAME'),
        }
        response = client.post(
            '/admin/user',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('admin_invalid' in error)
        self.assertEqual(response.status_code, 403)

# /admin/user - exception tests

    @patch('cassy.get_user_info')
    def test_user_info_unknown_exception(self, cassy_mock):
        """
        Tests the /admin/user endpoint when
        cassy.get_user_info throws Exception.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'request_username': os.environ.get('LOGIN_USERNAME'),
        }
        response = client.post(
            '/admin/user',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        cassy_mock.assert_called_once_with(
            payload.get('request_username', '')
        )
        self.assertEqual(response.status_code, 500)

    @patch('cassy.verify_authenticated_admin')
    def test_user_info_unknown_admin_exception(self, cassy_mock):
        """
        Tests the /admin/user endpoint when
        cassy.verify_authenticated_admin throws Exception.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'request_username': os.environ.get('LOGIN_USERNAME'),
        }
        response = client.post(
            '/admin/user',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        cassy_mock.assert_called_once_with(
            payload.get('auth_token', '')
        )
        self.assertEqual(response.status_code, 500)

# /admin/user - invalid HTTP method tests

    def test_user_info_invalid_method(self):
        """
        Tests the user info endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/admin/user')
        self.assertEqual(response.status_code, 405)

# /admin/user/subscription - valid request tests

    def test_user_update_sub_end_date(self):
        """
        Tests a valid request to update a user subscription date.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'request_username': os.environ.get('LOGIN_USERNAME'),
            'sub_end_date': '2100-01-01',
        }
        response = client.post(
            '/admin/user/subscription',
            data=json.dumps(payload),
            content_type='application/json'
        )
        body = json.loads(response.content.decode('utf-8'))
        self.assertTrue(body is not None)
        self.assertEqual(response.status_code, 200)

# /admin/user/subscription - invalid request tests

    def test_user_update_sub_end_date_invalid_username(self):
        """
        Tests a request to update a user subscription date
        with an invalid username.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'request_username': 'thisGuyAintInThere',
            'sub_end_date': '2100-01-01',
        }
        response = client.post(
            '/admin/user/subscription',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('username_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_user_update_sub_end_date_invalid_admin(self):
        """
        Tests a request to update a user subscription date
        with invalid admin credentials.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': 'thisWontGetYouFar',
            'request_username': os.environ.get('LOGIN_USERNAME'),
            'sub_end_date': '2100-01-01',
        }
        response = client.post(
            '/admin/user/subscription',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('admin_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_user_update_sub_end_date_invalid_format(self):
        """
        Tests a request to update a user subscription date
        with an invalid subscriptione end date: invalid format.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'request_username': os.environ.get('LOGIN_USERNAME'),
            'sub_end_date': '01-01-2100',
        }
        response = client.post(
            '/admin/user/subscription',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('sub_end_date_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_user_update_sub_end_date_invalid_format_long(self):
        """
        Tests a request to update a user subscription date
        with an invalid subscriptione end date: invalid format - too long.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'request_username': os.environ.get('LOGIN_USERNAME'),
            'sub_end_date': '01-01-2100-4000',
        }
        response = client.post(
            '/admin/user/subscription',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('sub_end_date_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_user_update_sub_end_date_invalid_characters(self):
        """
        Tests a request to update a user subscription date
        with an invalid subscriptione end date: invalid characters.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'request_username': os.environ.get('LOGIN_USERNAME'),
            'sub_end_date': '0!-o1-2100',
        }
        response = client.post(
            '/admin/user/subscription',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('sub_end_date_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_user_update_sub_end_date_invalid_date(self):
        """
        Tests a request to update a user subscription date
        with an invalid subscriptione end date: date in the past.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'request_username': os.environ.get('LOGIN_USERNAME'),
            'sub_end_date': '1800-01-01',
        }
        response = client.post(
            '/admin/user/subscription',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('sub_end_date_invalid' in error)
        self.assertEqual(response.status_code, 403)

# /admin/user/subscription exception tests

    @patch('cassy.update_user_subscription')
    def test_user_update_sub_end_date_unknown_exception(self, cassy_mock):
        """
        Tests the /admin/user/subscription endpoint when
        cassy.update_user_subscription throws Exception.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'request_username': os.environ.get('LOGIN_USERNAME'),
            'sub_end_date': '2100-01-01',
        }
        response = client.post(
            '/admin/user/subscription',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        cassy_mock.assert_called_once_with(
            payload.get('request_username', ''),
            payload.get('sub_end_date', '')
        )
        self.assertEqual(response.status_code, 500)

# /admin/user/subscription - invalid HTTP method tests

    def test_user_update_sub_end_date_invalid_method(self):
        """
        Tests the update user subscription end date endpoint
        with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/admin/user/subscription')
        self.assertEqual(response.status_code, 405)

# /admin/user/edit - valid request tests

    def test_edit_user(self):
        """
        Tests a valid request to edit a user.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'edit_user_info': {
                'username': os.environ.get('LOGIN_USERNAME'),
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
            },
        }
        response = client.post(
            '/admin/user/edit',
            data=json.dumps(payload),
            content_type='application/json'
        )
        body = json.loads(response.content.decode('utf-8'))
        self.assertTrue(body is not None)
        self.assertEqual(response.status_code, 200)

# /admin/user/edit - invalid request tests

    def test_edit_user_invalid_admin(self):
        """
        Tests a request to edit a user with invalid admin credentials.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': 'thisWontGetYouFar',
            'edit_user_info': {
                'username': os.environ.get('LOGIN_USERNAME'),
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
            },
        }
        response = client.post(
            '/admin/user/edit',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('admin_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_edit_user_invalid_username(self):
        """
        Tests a request to edit a user with an invalid username.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'edit_user_info': {
                'username': 'thisGuyAintInThere',
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
            },
        }
        response = client.post(
            '/admin/user/edit',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('username_invalid' in error)
        self.assertEqual(response.status_code, 403)

# /admin/user/edit exception tests

    @patch('cassy.edit_user')
    def test_edit_user_unknown_exception(self, cassy_mock):
        """
        Tests the /admin/user/edit endpoint when
        cassy.edit_user throws Exception.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'edit_user_info': {
                'username': os.environ.get('LOGIN_USERNAME'),
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
            },
        }
        response = client.post(
            '/admin/user/edit',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        cassy_mock.assert_called_once_with(
            payload.get('edit_user_info', '')
        )
        self.assertEqual(response.status_code, 500)

# /admin/user/edit - invalid HTTP method tests

    def test_edit_user_invalid_method(self):
        """
        Tests the edit user endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/admin/user/edit')
        self.assertEqual(response.status_code, 405)

# /admin/user/new - valid request tests

    @patch('admin.views.check_user_id')
    @patch('admin.views.check_username')
    def test_new_user(self, check_name_mock, check_id_mock):
        """
        Tests a valid request to create a new user.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': os.environ.get('LOGIN_USERNAME'),
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
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
        new_user_info = payload.get('new_user_info', '')
        user_id = str(new_user_info.get('userid', ''))
        username = str(new_user_info.get('username', ''))
        check_name_mock.assert_called_once_with(username)
        check_id_mock.assert_called_once_with(user_id)
        body = json.loads(response.content.decode('utf-8'))
        self.assertTrue(body is not None)
        self.assertEqual(response.status_code, 200)

# /admin/user/new - invalid request tests

    def test_new_user_invalid_admin(self):
        """
        Tests a request to create a new user with invalid admin credentials.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': 'thisWontGetYouFar',
            'new_user_info': {
                'username': os.environ.get('LOGIN_USERNAME'),
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
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
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('admin_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_new_user_invalid_characters(self):
        """
        Tests a request to create a new user with invalid username.
        The username contains non-alphanumeric characters.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': "th!$ gUy-i$-n0-g00D!!",
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
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
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('username_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_new_user_invalid_username_missing(self):
        """
        Tests a request to create a new user with invalid username.
        The username is missing from the request.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
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
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('data_missing' in error)
        self.assertEqual(response.status_code, 403)

    def test_new_user_invalid_username_taken(self):
        """
        Tests a request to create a new user with invalid username.
        The username already exists.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': os.environ.get('LOGIN_USERNAME'),
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
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
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('username_taken' in error)
        self.assertEqual(response.status_code, 403)

    def test_new_user_invalid_user_id_negative(self):
        """
        Tests a request to create a new user with invalid user id.
        The user id is negative.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': "HiImTheNewGuy",
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
                'subenddate': os.environ.get('LOGIN_SUB_END_DATE'),
                'userid': -1,
                'vineyards': [int(os.environ.get('LOGIN_USER_ID'))],
            },
        }
        response = client.post(
            '/admin/user/new',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('user_id_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_new_user_invalid_user_id_noninteger(self):
        """
        Tests a request to create a new user with invalid user id.
        The user id is not an integer.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': "HiImTheNewGuy",
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
                'subenddate': os.environ.get('LOGIN_SUB_END_DATE'),
                'userid': 'ImNotAnInteger',
                'vineyards': [int(os.environ.get('LOGIN_USER_ID'))],
            },
        }
        response = client.post(
            '/admin/user/new',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('user_id_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_new_user_invalid_user_id_exists(self):
        """
        Tests a request to create a new user with invalid user id.
        The user id already exists.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': "HiImTheNewGuy",
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
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
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('user_id_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_new_user_invalid_email_format(self):
        """
        Tests a request to create a new user with invalid email.
        The email is an incorrect format.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': "HiImTheNewGuy",
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': 'ImTheNewGuyAtMrCool.com',
                'admin': False,
                'enable': True,
                'subenddate': os.environ.get('LOGIN_SUB_END_DATE'),
                'userid': 1234567890,
                'vineyards': [int(os.environ.get('LOGIN_USER_ID'))],
            },
        }
        response = client.post(
            '/admin/user/new',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('email_bad_error' in error)
        self.assertEqual(response.status_code, 403)

    def test_new_user_invalid_admin_type(self):
        """
        Tests a request to create a new user with invalid data types.
        The 'admin' parameter is an invalid data type.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': "HiImTheNewGuy",
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': 'NotABooleanDude',
                'enable': True,
                'subenddate': os.environ.get('LOGIN_SUB_END_DATE'),
                'userid': 1234567890,
                'vineyards': [int(os.environ.get('LOGIN_USER_ID'))],
            },
        }
        response = client.post(
            '/admin/user/new',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('data_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_new_user_invalid_enable_type(self):
        """
        Tests a request to create a new user with invalid data types.
        The 'enable' parameter is an invalid data type.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': "HiImTheNewGuy",
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': 'NotABooleanDude',
                'subenddate': os.environ.get('LOGIN_SUB_END_DATE'),
                'userid': 1234567890,
                'vineyards': [int(os.environ.get('LOGIN_USER_ID'))],
            },
        }
        response = client.post(
            '/admin/user/new',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('data_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_new_user_invalid_vineyard_ids(self):
        """
        Tests a request to create a new user with invalid vineyard ids.
        The vineyards ids are negative.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': "HiImTheNewGuy",
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
                'subenddate': os.environ.get('LOGIN_SUB_END_DATE'),
                'userid': 1234567890,
                'vineyards': [-1],
            },
        }
        response = client.post(
            '/admin/user/new',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_bad_id' in error)
        self.assertEqual(response.status_code, 403)

# /admin/user/new exception tests

    @patch('cassy.create_new_user')
    @patch('admin.views.check_user_id')
    @patch('admin.views.check_username')
    def test_new_user_unknown_exception(self, check_name_mock, check_id_mock, cassy_mock):
        """
        Tests the /admin/user/new endpoint when
        cassy.create_new_user throws Exception.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': os.environ.get('LOGIN_USERNAME'),
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
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
        error = json.loads(response.content.decode('utf-8'))['errors']
        new_user_info = payload.get('new_user_info', '')
        user_id = str(new_user_info.get('userid', ''))
        username = str(new_user_info.get('username', ''))
        check_name_mock.assert_called_once_with(username)
        check_id_mock.assert_called_once_with(user_id)
        self.assertTrue('unknown' in error)
        cassy_mock.assert_called_once_with(
            payload.get('new_user_info', '')
        )
        self.assertEqual(response.status_code, 500)

    @patch('admin.views.check_username')
    @patch('admin.views.check_user_parameters')
    def test_new_user_value_error_exception(self, check_params_mock, check_name_mock):
        """
        Tests the /admin/user/new endpoint when
        admin.views.check_user_parameters throws ValueError.
        """
        setup_test_environment()
        client = Client()
        check_params_mock.side_effect = ValueError('Test ValueError')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': os.environ.get('LOGIN_USERNAME'),
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
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
        error = json.loads(response.content.decode('utf-8'))['errors']
        new_user_info = payload.get('new_user_info', '')
        username = str(new_user_info.get('username', ''))
        check_name_mock.assert_called_once_with(username)
        check_params_mock.assert_called_once_with(
            payload.get('new_user_info', '')
        )
        self.assertTrue('user_id_invalid' in error)
        self.assertEqual(response.status_code, 403)

    @patch('admin.views.check_username')
    def test_new_user_unknown_check_exception(self, check_user_mock):
        """
        Tests the /admin/user/new endpoint when
        admin.views.check_username throws Exception.
        """
        setup_test_environment()
        client = Client()
        check_user_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': os.environ.get('LOGIN_USERNAME'),
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
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
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        new_user_info = payload.get('new_user_info', '')
        check_user_mock.assert_called_once_with(
            new_user_info.get('username', '')
        )
        self.assertEqual(response.status_code, 500)

    @patch('admin.views.check_user_id')
    def test_new_user_unknown_check_id_exception(self, check_id_mock):
        """
        Tests the /admin/user/new endpoint when
        admin.views.check_user_id throws Exception.
        """
        setup_test_environment()
        client = Client()
        check_id_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': "HiImTheNewGuy",
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
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
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        new_user_info = payload.get('new_user_info', '')
        check_id_mock.assert_called_once_with(
            new_user_info.get('userid', '')
        )
        self.assertEqual(response.status_code, 500)

    @patch('cassy.check_user_id_exists')
    def test_new_user_unknown_check_id_cassy_exception(self, cassy_mock):
        """
        Tests the /admin/user/new endpoint when
        cassy.check_user_id_exists throws Exception.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': "HiImTheNewGuy",
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
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
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        new_user_info = payload.get('new_user_info', '')
        cassy_mock.assert_called_once_with(
            int(new_user_info.get('userid', ''))
        )
        self.assertEqual(response.status_code, 500)

    @patch('cassy.check_username_exists')
    def test_new_user_unknown_check_username_cassy_exception(self, cassy_mock):
        """
        Tests the /admin/user/new endpoint when
        check_username_existsthrows Exception.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_user_info': {
                'username': "HiImTheNewGuy",
                'password': os.environ.get('LOGIN_PASSWORD'),
                'email': os.environ.get('RESET_EMAIL'),
                'admin': False,
                'enable': True,
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
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        new_user_info = payload.get('new_user_info', '')
        cassy_mock.assert_called_once_with(
            new_user_info.get('username', '')
        )
        self.assertEqual(response.status_code, 500)

# /admin/user/new - invalid HTTP method tests

    def test_new_user_invalid_method(self):
        """
        Tests the create new user endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/admin/user/new')
        self.assertEqual(response.status_code, 405)

# /admin/user/disable - valid request tests

    def test_disable_user(self):
        """
        Tests a valid request to disable a user.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'request_username': os.environ.get('LOGIN_USERNAME'),
        }
        response = client.post(
            '/admin/user/disable',
            data=json.dumps(payload),
            content_type='application/json'
        )
        body = json.loads(response.content.decode('utf-8'))
        self.assertTrue(body is not None)
        self.assertEqual(response.status_code, 200)

# /admin/user/disable - invalid request tests

    def test_user_disable_invalid_username(self):
        """
        Tests a request to disable a user with an invalid username.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'request_username': 'thisGuyAintInThere',
        }
        response = client.post(
            '/admin/user/disable',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('username_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_user_disable_invalid_admin(self):
        """
        Tests a request to disable a user with an invalid admin credentials.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': 'thisWontGetYouFar',
            'request_username': os.environ.get('LOGIN_USERNAME'),
        }
        response = client.post(
            '/admin/user/disable',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('admin_invalid' in error)
        self.assertEqual(response.status_code, 403)

# /admin/user/disable exception tests

    @patch('cassy.disable_user')
    def test_user_disable_unknown_exception(self, cassy_mock):
        """
        Tests the /admin/user/disable endpoint when
        cassy.disable_user throws Exception.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'request_username': os.environ.get('LOGIN_USERNAME'),
        }
        response = client.post(
            '/admin/user/disable',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        cassy_mock.assert_called_once_with(
            payload.get('request_username', '')
        )
        self.assertEqual(response.status_code, 500)

# /admin/user/disable - invalid HTTP method tests

    def test_disable_user_invalid_method(self):
        """
        Tests the disable user endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/admin/user/disable')
        self.assertEqual(response.status_code, 405)

# /admin/vineyard - valid request tests

    def test_vineyard_info(self):
        """
        Tests a valid request for vineyard info.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'vineyard_id': os.environ.get('VINE_ID'),
        }
        response = client.post(
            '/admin/vineyard',
            data=json.dumps(payload),
            content_type='application/json'
        )
        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(
            content.get('name', ''),
            os.environ.get('VINE_NAME')
        )
        self.assertEqual(response.status_code, 200)

# /admin/vineyard - invalid request tests

    def test_vineyard_info_invalid_vineyard(self):
        """
        Tests a request for vineyard info with an invalid vineyard id.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'vineyard_id': 12345,
        }
        response = client.post(
            '/admin/vineyard',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_id_not_found' in error)
        self.assertEqual(response.status_code, 403)

    def test_vineyard_info_invalid_vineyard_negative(self):
        """
        Tests a request for vineyard info with an invalid vineyard id.
        The vineyard id is negative.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'vineyard_id': -1,
        }
        response = client.post(
            '/admin/vineyard',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_bad_id' in error)
        self.assertEqual(response.status_code, 403)

    def test_vineyard_info_invalid_admin(self):
        """
        Tests a request for vineyard info with an invalid admin credentials.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': 'thisWontGetYouFar',
            'vineyard_id': os.environ.get('VINE_ID'),
        }
        response = client.post(
            '/admin/vineyard',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('admin_invalid' in error)
        self.assertEqual(response.status_code, 403)

# /admin/vineyard - exception tests

    @patch('cassy.get_vineyard_info')
    def test_vineyard_info_unknown_exception(self, cassy_mock):
        """
        Tests the /admin/vineyard endpoint when
        cassy.get_user_info throws Exception.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'vineyard_id': os.environ.get('VINE_ID'),
        }
        response = client.post(
            '/admin/vineyard',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        cassy_mock.assert_called_once_with(
            payload.get('vineyard_id', '')
        )
        self.assertEqual(response.status_code, 500)

# /admin/vineyard - invalid HTTP method tests

    def test_vineyard_info_invalid_method(self):
        """
        Tests the vineyard info endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/admin/vineyard')
        self.assertEqual(response.status_code, 405)

# /admin/vineyard/new - valid request tests

    @patch('admin.views.check_vineyard_id')
    def test_new_vineyard(self, check_id_mock):
        """
        Tests a valid request to create a new vineyard.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_vineyard_info': {
                'vineyard_id': os.environ.get('VINE_ID'),
                'owners': [str(os.environ.get('VINE_OWNERS'))],
                'enable': True,
                'name': os.environ.get('VINE_NAME'),
                'boundaries': [{
                    'lat': os.environ.get('VINE_BOUND_LAT'),
                    'lon': os.environ.get('VINE_BOUND_LON'),
                }],
                'center': {
                    'lat': os.environ.get('VINE_CENTER_LAT'),
                    'lon': os.environ.get('VINE_CENTER_LON'),
                },
            },
        }
        response = client.post(
            '/admin/vineyard/new',
            data=json.dumps(payload),
            content_type='application/json'
        )
        new_vineyard_info = payload.get('new_vineyard_info', '')
        vineyard_id = str(new_vineyard_info.get('vineyard_id', ''))
        check_id_mock.assert_called_once_with(
             vineyard_id
        )
        body = json.loads(response.content.decode('utf-8'))
        self.assertTrue(body is not None)
        self.assertEqual(response.status_code, 200)

# /admin/vineyard/new - invalid request tests

    def test_new_vineyard_invalid_id_exists(self):
        """
        Tests an invalid request to create a new vineyard.
        The vineyard id already exists.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_vineyard_info': {
                'vineyard_id': os.environ.get('VINE_ID'),
                'owners': [str(os.environ.get('VINE_OWNERS'))],
                'enable': True,
                'name': os.environ.get('VINE_NAME'),
                'boundaries': [{
                    'lat': os.environ.get('VINE_BOUND_LAT'),
                    'lon': os.environ.get('VINE_BOUND_LON'),
                }],
                'center': {
                    'lat': os.environ.get('VINE_CENTER_LAT'),
                    'lon': os.environ.get('VINE_CENTER_LON'),
                },
            },
        }
        response = client.post(
            '/admin/vineyard/new',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_id_invalid' in error)
        self.assertEqual(response.status_code, 403)

    @patch('admin.views.check_vineyard_id')
    def test_new_vineyard_invalid_enable_type(self, check_id_mock):
        """
        Tests an invalid request to create a new vineyard.
        The enable is an invalid data type.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_vineyard_info': {
                'vineyard_id': os.environ.get('VINE_ID'),
                'owners': [str(os.environ.get('VINE_OWNERS'))],
                'enable': 'ImNotABoolean',
                'name': os.environ.get('VINE_NAME'),
                'boundaries': [{
                    'lat': os.environ.get('VINE_BOUND_LAT'),
                    'lon': os.environ.get('VINE_BOUND_LON'),
                }],
                'center': {
                    'lat': os.environ.get('VINE_CENTER_LAT'),
                    'lon': os.environ.get('VINE_CENTER_LON'),
                },
            },
        }
        response = client.post(
            '/admin/vineyard/new',
            data=json.dumps(payload),
            content_type='application/json'
        )
        new_vineyard_info = payload.get('new_vineyard_info', '')
        vineyard_id = str(new_vineyard_info.get('vineyard_id', ''))
        check_id_mock.assert_called_once_with(
             vineyard_id
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('data_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_new_vineyard_invalid_admin(self):
        """
        Tests a request to create a new vineyard
        with invalid admin credentials.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': 'thisWontGetYouFar',
            'new_vineyard_info': {
                'vineyard_id': os.environ.get('VINE_ID'),
                'owners': [str(os.environ.get('VINE_OWNERS'))],
                'enable': True,
                'name': os.environ.get('VINE_NAME'),
                'boundaries': [{
                    'lat': os.environ.get('VINE_BOUND_LAT'),
                    'lon': os.environ.get('VINE_BOUND_LON'),
                }],
                'center': {
                    'lat': os.environ.get('VINE_CENTER_LAT'),
                    'lon': os.environ.get('VINE_CENTER_LON'),
                },
            },
        }
        response = client.post(
            '/admin/vineyard/new',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('admin_invalid' in error)
        self.assertEqual(response.status_code, 403)

# /admin/vineyard/new exception tests

    @patch('cassy.create_new_vineyard')
    @patch('admin.views.check_vineyard_id')
    def test_new_vineyard_unknown_exception(self, check_id_mock, cassy_mock):
        """
        Tests the /admin/vineyard/new endpoint when
        cassy.create_new_vineyard throws Exception.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'new_vineyard_info': {
                'vineyard_id': os.environ.get('VINE_ID'),
                'owners': [str(os.environ.get('VINE_OWNERS'))],
                'enable': True,
                'name': os.environ.get('VINE_NAME'),
                'boundaries': [{
                    'lat': os.environ.get('VINE_BOUND_LAT'),
                    'lon': os.environ.get('VINE_BOUND_LON'),
                }],
                'center': {
                    'lat': os.environ.get('VINE_CENTER_LAT'),
                    'lon': os.environ.get('VINE_CENTER_LON'),
                },
            },
        }
        response = client.post(
            '/admin/vineyard/new',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        new_vineyard_info = payload.get('new_vineyard_info', '')
        vineyard_id = str(new_vineyard_info.get('vineyard_id', ''))
        check_id_mock.assert_called_once_with(
             vineyard_id
        )
        self.assertTrue('unknown' in error)
        cassy_mock.assert_called_once_with(
            payload.get('new_vineyard_info', '')
        )
        self.assertEqual(response.status_code, 500)

        # /admin/user/new - invalid HTTP method tests

    def test_new_vineyard_invalid_method(self):
        """
        Tests the create new vineyard endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/admin/vineyard/new')
        self.assertEqual(response.status_code, 405)

# /admin/vineyard/edit - valid request tests

    def test_edit_vineyard(self):
        """
        Tests a valid request to edit a vineyard.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'edit_vineyard_info': {
                'vineyard_id': os.environ.get('VINE_ID'),
                'owners': [str(os.environ.get('VINE_OWNERS'))],
                'name': os.environ.get('VINE_NAME'),
            },
        }
        response = client.post(
            '/admin/vineyard/edit',
            data=json.dumps(payload),
            content_type='application/json'
        )
        body = json.loads(response.content.decode('utf-8'))
        self.assertTrue(body is not None)
        self.assertEqual(response.status_code, 200)

# /admin/vineyard/edit - invalid request tests

    def test_edit_vineyard_invalid_admin(self):
        """
        Tests a request to create a new vineyard
        with invalid admin credentials.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': 'thisWontGetYouFar',
            'edit_vineyard_info': {
                'vineyard_id': os.environ.get('VINE_ID'),
                'owners': [str(os.environ.get('VINE_OWNERS'))],
                'name': os.environ.get('VINE_NAME'),
            },
        }
        response = client.post(
            '/admin/vineyard/edit',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('admin_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_edit_vineyard_invalid_vineyard_id_nonexistent(self):
        """
        Tests a request to edit a vineyard with an invalid vineyard id.
        The vineyard id does not exist.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'edit_vineyard_info': {
                'vineyard_id': 1234567890,
                'owners': [str(os.environ.get('VINE_OWNERS'))],
                'name': os.environ.get('VINE_NAME'),
            },
        }
        response = client.post(
            '/admin/vineyard/edit',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_id_not_found' in error)
        self.assertEqual(response.status_code, 403)

    def test_edit_vineyard_invalid_vineyard_id_negative(self):
        """
        Tests a request to edit a vineyard with an invalid vineyard id.
        The vineyard id is negative.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'edit_vineyard_info': {
                'vineyard_id': -1,
                'owners': [str(os.environ.get('VINE_OWNERS'))],
                'name': os.environ.get('VINE_NAME'),
            },
        }
        response = client.post(
            '/admin/vineyard/edit',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_id_invalid' in error)
        self.assertEqual(response.status_code, 403)

    def test_edit_vineyard_invalid_enable_type(self):
        """
        Tests a request to edit a vineyard with an invalid enable value.
        The enable value is an inavlid data type.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'edit_vineyard_info': {
                'vineyard_id': os.environ.get('VINE_ID'),
                'owners': [str(os.environ.get('VINE_OWNERS'))],
                'name': os.environ.get('VINE_NAME'),
                'enable': "ImNotABoolean",
            },
        }
        response = client.post(
            '/admin/vineyard/edit',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('data_invalid' in error)
        self.assertEqual(response.status_code, 403)

# /admin/vineyard/edit exception tests

    @patch('cassy.edit_vineyard')
    def test_edit_vineyard_unknown_exception(self, cassy_mock):
        """
        Tests the /admin/vineyard/edit endpoint when
        cassy.edit_vineyard throws Exception.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'edit_vineyard_info': {
                'vineyard_id': os.environ.get('VINE_ID'),
                'owners': [str(os.environ.get('VINE_OWNERS'))],
                'name': os.environ.get('VINE_NAME'),
            },
        }
        response = client.post(
            '/admin/vineyard/edit',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        cassy_mock.assert_called_once_with(
            payload.get('edit_vineyard_info', '')
        )
        self.assertEqual(response.status_code, 500)

        # /admin/user/new - invalid HTTP method tests

    def test_edit_vineyard_invalid_method(self):
        """
        Tests the edit vineyard endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/admin/vineyard/edit')
        self.assertEqual(response.status_code, 405)

# /admin/vineyard/disable - valid request tests

    def test_disable_vineyard(self):
        """
        Tests a valid request to disable a vineyard.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'vineyard_id': os.environ.get('VINE_ID'),
        }
        response = client.post(
            '/admin/vineyard/disable',
            data=json.dumps(payload),
            content_type='application/json'
        )
        body = json.loads(response.content.decode('utf-8'))
        self.assertTrue(body is not None)
        self.assertEqual(response.status_code, 200)

# /admin/vineyard/disable - invalid request tests

    def test_vineyard_disable_invalid_vineyard(self):
        """
        Tests a request to disable a vineyard with an invalid vineyard id.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'vineyard_id': 12345,
        }
        response = client.post(
            '/admin/vineyard/disable',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_bad_id' in error)
        self.assertEqual(response.status_code, 403)

    def test_vineyard_disable_invalid_admin(self):
        """
        Tests a request to disable a vineyard with invalid admin credentials.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': 'thisWontGetYouFar',
            'vineyard_id': os.environ.get('VINE_ID'),
        }
        response = client.post(
            '/admin/vineyard/disable',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('admin_invalid' in error)
        self.assertEqual(response.status_code, 403)

# /admin/vineyard/disable exception tests

    @patch('cassy.disable_vineyard')
    def test_vineyard_disable_unknown_exception(self, cassy_mock):
        """
        Tests the /admin/vineyard/disable endpoint when
        cassy.disable_vineyard throws Exception.
        """
        setup_test_environment()
        client = Client()
        cassy_mock.side_effect = Exception('Test exception')
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'vineyard_id': os.environ.get('VINE_ID'),
        }
        response = client.post(
            '/admin/vineyard/disable',
            data=json.dumps(payload),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('unknown' in error)
        cassy_mock.assert_called_once_with(
            payload.get('vineyard_id', '')
        )
        self.assertEqual(response.status_code, 500)

# /admin/vineyard/disable - invalid HTTP method tests

    def test_disable_vineyard_invalid_method(self):
        """
        Tests the disable vineyard endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/admin/vineyard/disable')
        self.assertEqual(response.status_code, 405)
