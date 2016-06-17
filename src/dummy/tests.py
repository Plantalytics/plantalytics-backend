from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.http.response import HttpResponseRedirect

# Create your tests here.

class MainTests(TestCase):


    def test_http_response(self):
        setup_test_environment()
        client = Client()
        response = client.get('/dummy/')
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
