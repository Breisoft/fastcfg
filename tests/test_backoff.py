import unittest

from fastcfg.backoff import exponential_backoff
from fastcfg.backoff.policies import BackoffPolicy


class TestExponentialBackoff(unittest.TestCase):

    def test_immediate_success(self):
        """Function should return immediately if no exceptions are raised."""
        @exponential_backoff(backoff_policy=BackoffPolicy(max_retries=3, base_delay=1, max_delay=10, factor=2, jitter=False))
        def successful_function():
            return "Success"

        result = successful_function()
        self.assertEqual(result, "Success")
