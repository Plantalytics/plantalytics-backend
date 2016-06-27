#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

import os

from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.http.response import HttpResponseRedirect


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
        response = client.get(
            '/login/?username='
            + os.environ.get('LOGIN_USERNAME')
            + '&password='
            + os.environ.get('LOGIN_PASSWORD')
        )
        self.assertEqual(response.status_code, 200)

    def test_response_invalid_username(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/login/?username=mrawesome'
            + '&password='
            + os.environ.get('LOGIN_PASSWORD')
        )
        self.assertEqual(response.status_code, 403)

    def test_response_invalid_password(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/login/?username='
            + os.environ.get('LOGIN_USERNAME')
            + '&password=notcorrect'
        )
        self.assertEqual(response.status_code, 403)

    def test_response_temperature_data(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data/'
            + '?vineyard_id=0&'
            + 'env_variable=temperature'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_humidity_data(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data/'
            + '?vineyard_id=0&'
            + 'env_variable=humidity'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_leafwetness_data(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data/'
            + '?vineyard_id=0&'
            + 'env_variable=leafwetness'
        )
        self.assertEqual(response.status_code, 200)

    def test_response_invlaid_vineyard(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data/'
            + '?vineyard_id=101&'
            + 'env_variable=temperature'
        )
        self.assertEqual(response.status_code, 400)

    def test_response_invlaid_env_variable(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data/'
            + '?vineyard_id=0&'
            + 'env_variable=cheesiness'
        )
        self.assertEqual(response.status_code, 400)

    def test_response_invlaid_env_data_request(self):
        setup_test_environment()
        client = Client()
        response = client.get(
            '/env_data/'
            + '?vineyard_id=101&'
            + 'env_variable=cheesiness'
        )
        self.assertEqual(response.status_code, 400)

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
