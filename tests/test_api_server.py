import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api.server import app

class TestAPIAuth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_missing_api_key(self):
        """Test API requests without an API key header"""
        response = self.client.get("/scans/test-target")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Not authenticated")

    @patch('api.server.auth_manager.verify_api_key')
    def test_invalid_api_key(self, mock_verify):
        """Test API requests with an invalid API key"""
        mock_verify.return_value = None

        response = self.client.get("/scans/test-target", headers={"X-API-Key": "invalid_key"})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid API key")
        mock_verify.assert_called_once_with("invalid_key")

    @patch('api.server.auth_manager.verify_api_key')
    @patch('api.server.db_manager.get_scan_history')
    def test_valid_api_key(self, mock_get_scan_history, mock_verify):
        """Test API requests with a valid API key"""
        mock_verify.return_value = {
            "username": "test_user",
            "roles": ["user"],
            "permissions": ["view"]
        }
        mock_get_scan_history.return_value = {"scans": []}

        response = self.client.get("/scans/test-target", headers={"X-API-Key": "valid_key"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"scans": []})
        mock_verify.assert_called_once_with("valid_key")
        mock_get_scan_history.assert_called_once_with("test-target")

if __name__ == '__main__':
    unittest.main()
