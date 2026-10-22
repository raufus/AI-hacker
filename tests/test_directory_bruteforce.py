"""
Tests for directory bruteforce module
"""
import unittest
from unittest.mock import patch
import requests
from modules.directory_bruteforce import DirectoryBruteforcer

class TestDirectoryBruteforcer(unittest.TestCase):
    def setUp(self):
        self.bruteforcer = DirectoryBruteforcer()

    @patch('requests.Session.get')
    def test_check_path_error_handling(self, mock_get):
        """Test error handling in check_path when a request fails"""
        # Configure the mock to raise a Timeout exception
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        # Call the method
        base_url = "http://example.com"
        path = "admin"
        result = self.bruteforcer.check_path(base_url, path)

        # Verify the results
        self.assertEqual(result["url"], "http://example.com/admin")
        self.assertFalse(result["exists"])
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Connection timed out")

        # Ensure the mock was called with correct parameters
        mock_get.assert_called_once_with(
            "http://example.com/admin",
            timeout=10,
            allow_redirects=False
        )

if __name__ == '__main__':
    unittest.main()
