import unittest2
import webtest

import webapp2
from main import app

class TestBase(unittest2.TestCase):
    """
    Base test class, any request handler test should
    extends this.
    """

    def setUp(self):
        """Just setup web client"""

        self.client = webtest.TestApp(app)