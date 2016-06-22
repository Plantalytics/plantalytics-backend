from django.test import TestCase, Client
from django.test.utils import setup_test_environment

# Create your tests here.

class MainTests(TestCase):


    def test_response_data(self):
        setup_test_environment()
        client = Client()
        response = client.get('/env_data/1/1/')
        self.assertEqual(response.status_code, 200)
