"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from vendors.iii.settings import *

class ConfigurationTest(TestCase):

    def test_opac_settings(self):
        self.assertEquals(OPAC_URL,
                          'http://tiger.coloradocollege.edu')

