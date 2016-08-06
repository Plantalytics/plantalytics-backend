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


class MainTests(TestCase):
    """
    Executes all of the unit tests for the vineyard endpoint.
    """

    def test_response_vineyard_metadata(self):
        """
        Tests the vineyard endpoint with valid vineyard id and auth token.
        """
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
        }
        response = client.post(
            '/vineyard',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_vineyard_metadata_invalid_method(self):
        """
        Tests the vineyard endpoint with unsupported HTTP method.
        """
        setup_test_environment()
        client = Client()
        response = client.get('/vineyard')
        self.assertEqual(response.status_code, 405)

    @patch('cassy.get_vineyard_coordinates')
    def test_response_vineyard_unknown_exception(self, vineyard_mock):
        """
        Tests vineyard endpoint when
        cassy.get_vineyard_coordinates throws Exception
        """
        setup_test_environment()
        client = Client()
        vineyard_mock.side_effect = Exception('Test exception')
        body = {
            'vineyard_id': '0',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
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
        """
        Tests the vineyard endpoint with invalid vineyard id
        and valid  token.
        """
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '-1',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
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
        """
        Tests the vineyard endpoint with valid auth token
        and missing vineyard id.
        """
        setup_test_environment()
        client = Client()
        body = {
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
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
        """
        Tests the vineyard endpoint with valid auth token
        and invalid vineyard id (invalid type - non-integer).
        """
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': 'abc',
            'auth_token': os.environ.get('LOGIN_SEC_TOKEN'),
        }
        response = client.post(
            '/vineyard',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('vineyard_bad_id' in error)
        self.assertEqual(response.status_code, 400)

    @patch('cassy.verify_auth_token')
    def test_response_vineyard_auth_unknown_exception(self, vineyard_mock):
        """
        Tests vineyard endpoint when
        cassy.verify_auth_token throws Exception
        """
        setup_test_environment()
        client = Client()
        vineyard_mock.side_effect = Exception('Test exception')
        body = {
            'vineyard_id': '0',
            'auth_token': 'chestercheetah',
        }
        response = client.post(
            '/vineyard',
            data=json.dumps(body),
            content_type='application/json'
        )
        error = json.loads(response.content.decode('utf-8'))['errors']
        self.assertTrue('auth_error_unknown' in error)
        self.assertEqual(response.status_code, 403)

    def test_response_vineyard_metadata_invalid_token(self):
        """
        Tests the vineyard endpoint with valid vineyard id
        and invalid auth token.
        """
        setup_test_environment()
        client = Client()
        body = {
            'vineyard_id': '0',
            'auth_token': 'chestercheetah',
        }
        response = client.post(
            '/vineyard',
            data=json.dumps(body),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
