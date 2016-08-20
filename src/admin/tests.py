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

    def test_edit_vineyard_invalid_username(self):
        """
        Tests a request to edit a vineyard with an invalid vineyard id.
        """
        setup_test_environment()
        client = Client()
        payload = {
            'auth_token': os.environ.get('ADMIN_TOKEN'),
            'edit_vineyard_info': {
                'vineyard_id': 12345,
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
        self.assertTrue('vineyard_bad_id' in error)
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
