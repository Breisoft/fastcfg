import unittest
from unittest.mock import patch
from fastcfg.sources.remote.network import RequestsLiveTracker
from fastcfg.exceptions import NetworkError
import requests

from fastcfg.config import Config

from fastcfg.sources.local import from_callable, from_os_environ

import os


class TestLocalSources(unittest.TestCase):

    def test_callable(self):
        """
        Test the callable source
        """

        def func(x): return x + 1

        config = Config()

        config.func = from_callable(func, 3)

        self.assertEqual(config.func, 4)

    def test_os_environ(self):
        """
        Test the os environ source
        """

        os.environ['TEST_ENV'] = 'test'
        config = Config()
        config.env = from_os_environ('TEST_ENV')
        self.assertEqual(config.env, 'test')
