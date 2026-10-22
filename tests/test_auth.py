import unittest
import tempfile
import os
from security.auth import AuthManager

class TestAuthManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary file to use as the auth file
        self.fd, self.auth_file = tempfile.mkstemp()
        # Ensure it's empty so AuthManager initializes with default data
        os.close(self.fd)
        if os.path.exists(self.auth_file):
            os.remove(self.auth_file)

        # Mock _setup_auth_system to avoid AttributeError since it's not implemented yet
        original_setup = getattr(AuthManager, '_setup_auth_system', None)
        AuthManager._setup_auth_system = lambda self: None
        try:
            self.auth_manager = AuthManager(auth_file=self.auth_file)
        finally:
            if original_setup:
                AuthManager._setup_auth_system = original_setup
            else:
                delattr(AuthManager, '_setup_auth_system')

    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.auth_file):
            os.remove(self.auth_file)

    def test_authenticate_user_success(self):
        """Test successful authentication with valid credentials"""
        self.assertTrue(self.auth_manager.authenticate_user("admin", "admin123"))

    def test_authenticate_user_incorrect_password(self):
        """Test authentication failure with incorrect password"""
        self.assertFalse(self.auth_manager.authenticate_user("admin", "wrongpassword"))

    def test_authenticate_user_nonexistent_user(self):
        """Test authentication failure with non-existent user"""
        self.assertFalse(self.auth_manager.authenticate_user("unknown", "admin123"))

if __name__ == '__main__':
    unittest.main()
