import os
import unittest

from fastcfg.config import Config
from fastcfg.exceptions import MissingEnvironmentVariableError
from fastcfg.sources.memory import from_callable, from_os_environ


class TestMemorySources(unittest.TestCase):

    def test_callable(self):
        """
        Test the callable source
        """

        def func(x):
            return x + 1

        config = Config()

        config.func = from_callable(func, 3)

        self.assertEqual(config.func, 4)

    def test_os_environ(self):
        """
        Test the os environ source
        """

        os.environ["TEST_ENV"] = "test"
        config = Config()
        config.env = from_os_environ("TEST_ENV")
        self.assertEqual(config.env, "test")

        # Delete the environment variable and then
        # make sure we get a MissingEnvironmentVariable Error
        del os.environ["TEST_ENV"]

        with self.assertRaises(MissingEnvironmentVariableError):
            str(config.env)
