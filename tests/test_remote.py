import unittest
from unittest.mock import patch
from fastcfg.sources.remote.network import RequestsLiveTracker
from fastcfg.exceptions import NetworkError
import requests


class TestRequestsLiveTracker(unittest.TestCase):
    """
    Test cases for the RequestsLiveTracker class.

    This class contains test methods to verify the behavior and functionality of the RequestsLiveTracker class,
    including handling of network exceptions and retry logic.
    """

    @patch('requests.get')
    def test_network_error_raises_exception(self, mock_get):
        """
        Test that a network error raises a NetworkError exception.
        """
        mock_get.side_effect = requests.exceptions.RequestException()
        tracker = RequestsLiveTracker('http://example.com', 'get')

        with self.assertRaises(NetworkError):
            tracker.get_state()

    @patch('requests.get')
    def test_no_retries_on_network_error(self, mock_get):
        """
        Test that the tracker does not retry on network errors when retry is disabled.
        """
        mock_get.side_effect = requests.exceptions.RequestException()
        tracker = RequestsLiveTracker('http://example.com', 'get', retry=False)

        # Ensure NetworkError is raised
        with self.assertRaises(NetworkError):
            tracker.get_state()

        # Ensure the mock_get method was only called once
        self.assertEqual(mock_get.call_count, 1)

    @patch('requests.get')
    def test_retry_on_network_error(self, mock_get):
        """
        Test that the tracker retries on network errors when retry is enabled
        and succeeds on the second attempt.
        """
        # Simulate a network error first and a success afterward.
        mock_get.side_effect = [
            requests.exceptions.RequestException(),
            'success'
        ]

        tracker = RequestsLiveTracker(
            'http://example.com', 'get', retry=True, max_retries=2)

        # Ensure that the state is successfully retrieved on the retry.
        state = tracker.get_state()
        self.assertEqual(state, 'success')
        self.assertEqual(mock_get.call_count, 2)
