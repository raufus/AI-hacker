"""
Tests for NetworkUtils
"""
import unittest
from utils.network_utils import NetworkUtils

class TestNetworkUtils(unittest.TestCase):
    def test_is_valid_domain_valid_domains(self):
        """Test is_valid_domain with valid domain names"""
        valid_domains = [
            "example.com",
            "www.example.com",
            "sub.sub.example.com",
            "example.co.uk",
            "a.com",
            "a-b.com",
            "example123.com",
            "123example.com",
            "example-domain.com",
            "example.org",
            "localhost"
        ]

        for domain in valid_domains:
            with self.subTest(domain=domain):
                self.assertTrue(NetworkUtils.is_valid_domain(domain))

    def test_is_valid_domain_invalid_domains(self):
        """Test is_valid_domain with invalid domain names"""
        invalid_domains = [
            "-example.com",
            "example-.com",
            "example..com",
            ".example.com",
            "example.com.",
            "ex ample.com",
            "example_domain.com",
            "example.com/path",
            "http://example.com",
            "example@com",
            "",
            "a" * 64 + ".com", # label too long (max 63 characters, a*64 is 64 characters)
        ]

        for domain in invalid_domains:
            with self.subTest(domain=domain):
                self.assertFalse(NetworkUtils.is_valid_domain(domain))

if __name__ == '__main__':
    unittest.main()
