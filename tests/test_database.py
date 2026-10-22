"""
Comprehensive tests for database management
"""
import unittest
import os
import sqlite3
import tempfile
import shutil
from database.database import DatabaseManager

class TestDatabaseSetup(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for database files
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_hackeros.db")

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_setup_database_creates_file_and_dir(self):
        """Test that _setup_database creates the DB file and directories."""
        # Use a nested path to test directory creation
        nested_db_path = os.path.join(self.test_dir, "nested", "test_hackeros.db")
        db = DatabaseManager(db_path=nested_db_path)

        self.assertTrue(os.path.exists(os.path.dirname(nested_db_path)))
        self.assertTrue(os.path.exists(nested_db_path))
        self.assertTrue(os.path.isfile(nested_db_path))

    def test_setup_database_creates_tables(self):
        """Test that _setup_database creates required tables."""
        db = DatabaseManager(db_path=self.db_path)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row[0] for row in cursor.fetchall()}

            # sqlite_sequence is created automatically by sqlite for autoincrement
            tables.discard('sqlite_sequence')

            self.assertIn('targets', tables)

    def test_setup_database_idempotent(self):
        """Test that _setup_database can be called multiple times without errors."""
        db = DatabaseManager(db_path=self.db_path)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables_before = {row[0] for row in cursor.fetchall()}

        # Call it again
        db._setup_database()

        # Verify it still works and didn't crash
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables_after = {row[0] for row in cursor.fetchall()}

            self.assertTrue(len(tables_after) > 0)
            self.assertEqual(tables_before, tables_after)

if __name__ == '__main__':
    unittest.main()
