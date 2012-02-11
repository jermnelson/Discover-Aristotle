"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import unittest
from settings import *

class ConfigurationTest(unittest.TestCase):

    def test_opac_settings(self):
        self.assertEquals(OPAC_URL,
                          'http://tiger.coloradocollege.edu/xrecord=')

