import unittest
from unittest.mock import patch, call
from fastcfg.backoff import exponential_backoff
from fastcfg.backoff.policies import BackoffPolicy
from fastcfg.exceptions import MaxRetriesExceededError

DEFAULT_BACKOFF_POLICY = BackoffPolicy(
    max_retries=3,
    base_delay=1,
    max_delay=10,
    factor=2,
    jitter=False
)

JITTER_BACKOFF_POLICY = BackoffPolicy(
    max_retries=3,
    base_delay=1,
    max_delay=10,
    factor=2,
    jitter=True
)


class TestExponentialBackoff(unittest.TestCase):

    def test_immediate_success(self):
        """Function should return immediately if no exceptions are raised."""
        @exponential_backoff(backoff_policy=DEFAULT_BACKOFF_POLICY)
        def successful_function():
            return "Success"

        result = successful_function()
        self.assertEqual(result, "Success")

    @patch('time.sleep', return_value=None)
    def test_retries_on_failure(self, mock_sleep):
        """Function should retry the specified number of times before raising an exception."""
        @exponential_backoff(backoff_policy=DEFAULT_BACKOFF_POLICY)
        def failing_function():
            raise ValueError("Failure")

        with self.assertRaises(MaxRetriesExceededError):
            failing_function()

        # Check that the function was called the expected number of times
        self.assertEqual(mock_sleep.call_count,
                         DEFAULT_BACKOFF_POLICY.max_retries - 1)

    @patch('time.sleep', return_value=None)
    def test_with_jitter(self, mock_sleep):
        """Function should include jitter in the backoff delay."""
        @exponential_backoff(backoff_policy=JITTER_BACKOFF_POLICY)
        def sometimes_failing_function():
            if sometimes_failing_function.attempts < 2:
                sometimes_failing_function.attempts += 1
                raise ValueError("Failure")
            return "Success"

        sometimes_failing_function.attempts = 0
        result = sometimes_failing_function()
        self.assertEqual(result, "Success")
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('time.sleep', return_value=None)
    def test_maximum_delay(self, mock_sleep):
        """Function should not exceed the maximum specified delay."""
        @exponential_backoff(backoff_policy=BackoffPolicy(max_retries=3, base_delay=1, max_delay=2, factor=2, jitter=False))
        def failing_function():
            raise ValueError("Failure")

        with self.assertRaises(MaxRetriesExceededError):
            failing_function()

        # Check that the function was called the expected number of times
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('time.sleep', return_value=None)
    def test_success_after_retries(self, mock_sleep):
        """Function should succeed after a few retries."""
        @exponential_backoff(backoff_policy=DEFAULT_BACKOFF_POLICY)
        def sometimes_failing_function():
            if sometimes_failing_function.attempts < 2:
                sometimes_failing_function.attempts += 1
                raise ValueError("Failure")
            return "Success"

        sometimes_failing_function.attempts = 0
        result = sometimes_failing_function()
        self.assertEqual(result, "Success")
        self.assertEqual(mock_sleep.call_count, 2)


if __name__ == '__main__':
    unittest.main()
