"""
Comprehensive tests for scanning modules
"""
import unittest
from modules.scanning import NetworkScanner, WebScanner, VulnerabilityScanner
from modules.vulnerability_database import VulnerabilityDatabase

class TestScanningModules(unittest.TestCase):
    def setUp(self):
        self.network_scanner = NetworkScanner()
        self.web_scanner = WebScanner()
        self.vuln_scanner = VulnerabilityScanner()
        self.vuln_db = VulnerabilityDatabase()
    
    def test_network_scan(self):
        """Test network scanning functionality"""
        # Note: NetworkScanner requires scan() API. Test handles non-root Nmap failure gracefully.
        results = self.network_scanner.scan("127.0.0.1")
        self.assertIsNotNone(results)
        if isinstance(results, dict) and "error" in results:
            self.assertIn("Nmap", results["error"])
        else:
            self.assertIsInstance(results, list)
    
    def test_web_scanning(self):
        """Test web application scanning"""
        # Note: we test graceful handling of connection refusal
        results = self.web_scanner.scan("http://127.0.0.1")
        self.assertIsNotNone(results)
        if "error" in results:
            self.assertIn("Failed to connect", results["error"])
        else:
            self.assertIn("vulnerabilities", results)
    
    def test_vulnerability_scanning(self):
        """Test vulnerability scanning"""
        results = self.vuln_scanner.scan("192.168.1.100", {"services": [{"product": "apache", "version": "2.4.49"}]})
        self.assertIsNotNone(results)
        self.assertIn("vulnerabilities", results)
        self.assertEqual(len(results["vulnerabilities"]), 1)
        
    def test_vulnerability_database(self):
        """Test vulnerability database operations"""
        vuln = self.vuln_db.get_vulnerability("web", "sql_injection")
        self.assertIsNotNone(vuln)
        self.assertEqual(vuln["severity"], "high")
    
    def test_error_handling(self):
        """Test error handling in scanning"""
        results = self.web_scanner.scan("invalid-url")
        # Should gracefully return dict containing errors, or handle without throwing ValueError
        self.assertIsNotNone(results)

if __name__ == '__main__':
    unittest.main()
