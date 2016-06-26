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


class MainTests(TestCase):
    """
    Executes all of the unit tests for the 'login' endpoint.
    """
    def test_response_login(self):
        setup_test_environment()
        client = Client()
        response = client.get('/login/'
                              + '?username='
                              + os.environ.get('LOGIN_USERNAME')
                              + '&password='
                              + os.environ.get('LOGIN_PASSWORD'))
        self.assertEqual(response.status_code, 200)

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
