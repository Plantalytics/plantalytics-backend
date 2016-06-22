from django.test import TestCase, Client
from django.test.utils import setup_test_environment

# Create your tests here.

class MainTests(TestCase):


    def test_response_temperature_data(self):
        setup_test_environment()
        client = Client()
        response = client.get('/env_data/0/temperature/')
        self.assertEqual(response.status_code, 200)

    def test_response_humidity_data(self):
        setup_test_environment()
        client = Client()
        response = client.get('/env_data/0/humidity/')
        self.assertEqual(response.status_code, 200)

    def test_response_leafwetness_data(self):
        setup_test_environment()
        client = Client()
        response = client.get('/env_data/0/leafwetness/')
        self.assertEqual(response.status_code, 200)
