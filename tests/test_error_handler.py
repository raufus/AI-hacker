import unittest
import tempfile
import os
import json
import logging
from unittest.mock import patch
from datetime import datetime
from utils.error_handler import ErrorHandler

class TestErrorHandler(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory and file path for the error database
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_error_db.json")

        # Patch the _setup_error_database to prevent the original __init__ from touching data/error_database.json
        with patch.object(ErrorHandler, '_setup_error_database'):
            self.handler = ErrorHandler(logging.getLogger("test"))

        # Manually set the database path and call setup
        self.handler.error_db = self.db_path
        self.handler._setup_error_database()

    def tearDown(self):
        # Clean up the temporary file and directory
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.test_dir)

    def test_setup_error_database(self):
        """Test that the database is initialized correctly"""
        self.assertTrue(os.path.exists(self.db_path))
        with open(self.db_path, 'r') as f:
            db = json.load(f)
        self.assertIn("errors", db)
        self.assertIsInstance(db["errors"], dict)
        self.assertIn("last_update", db)

    def test_update_error_database(self):
        """Test updating the error database with a new error"""
        test_error_data = {
            "type": "TestError",
            "message": "This is a test error",
            "timestamp": datetime.now().isoformat()
        }

        # Update the database
        self.handler._update_error_database(test_error_data)

        # Verify the file was updated
        with open(self.db_path, 'r') as f:
            db = json.load(f)

        self.assertEqual(len(db["errors"]), 1)

        # Check that the error was added with the correct ID format
        error_id = list(db["errors"].keys())[0]
        self.assertTrue(error_id.startswith("error_"))

        # Check the stored data matches what we inserted
        stored_error = db["errors"][error_id]
        self.assertEqual(stored_error["type"], "TestError")
        self.assertEqual(stored_error["message"], "This is a test error")

        # Check last_update was updated
        self.assertIn("last_update", db)
        self.assertIsInstance(db["last_update"], str)

    @patch('utils.error_handler.datetime')
    def test_update_error_database_multiple(self, mock_datetime):
        """Test adding multiple errors to the database"""
        # Create a mock datetime object that returns different times on successive strftime calls
        # We need two different string representations
        mock_now = mock_datetime.now.return_value
        mock_now.strftime.side_effect = ['20230101_120000', '20230101_120001']
        mock_now.isoformat.return_value = '2023-01-01T12:00:00'

        test_error_1 = {"type": "Error1", "message": "First error"}
        test_error_2 = {"type": "Error2", "message": "Second error"}

        self.handler._update_error_database(test_error_1)
        self.handler._update_error_database(test_error_2)

        with open(self.db_path, 'r') as f:
            db = json.load(f)

        self.assertEqual(len(db["errors"]), 2)

if __name__ == '__main__':
    unittest.main()
