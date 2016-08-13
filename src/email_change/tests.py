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
    Executes all of the unit tests for the env_data endpoint.
    """

    def test_place_holder(self):
        """
        Test env data endpoint when temperature data is requested.
        """
        pass
