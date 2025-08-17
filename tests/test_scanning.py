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
        results = self.network_scanner.scan_network("192.168.1.0/24")
        self.assertIsNotNone(results)
        self.assertIn("hosts", results)
        self.assertGreater(len(results["hosts"]), 0)
    
    def test_web_scanning(self):
        """Test web application scanning"""
        results = self.web_scanner.scan_web_app("http://test.local")
        self.assertIsNotNone(results)
        self.assertIn("vulnerabilities", results)
        self.assertIn("technologies", results)
    
    def test_vulnerability_scanning(self):
        """Test vulnerability scanning"""
        results = self.vuln_scanner.scan_target("192.168.1.100")
        self.assertIsNotNone(results)
        self.assertIn("critical", results)
        self.assertIn("high", results)
        
    def test_vulnerability_database(self):
        """Test vulnerability database operations"""
        vuln = self.vuln_db.get_vulnerability("web", "sql_injection")
        self.assertIsNotNone(vuln)
        self.assertEqual(vuln["severity"], "high")
    
    def test_scan_performance(self):
        """Test scanning performance"""
        import time
        start = time.time()
        self.network_scanner.scan_network("192.168.1.0/24")
        end = time.time()
        self.assertLess(end - start, 60)  # Should complete in less than 60 seconds
    
    def test_error_handling(self):
        """Test error handling in scanning"""
        with self.assertRaises(ValueError):
            self.web_scanner.scan_web_app("invalid-url")
    
    def test_resource_usage(self):
        """Test resource usage during scanning"""
        import psutil
        process = psutil.Process()
        mem_before = process.memory_info().rss
        self.network_scanner.scan_network("192.168.1.0/24")
        mem_after = process.memory_info().rss
        self.assertLess(mem_after - mem_before, 100 * 1024 * 1024)  # Should use less than 100MB
    
    def test_parallel_scanning(self):
        """Test parallel scanning capabilities"""
        from concurrent.futures import ThreadPoolExecutor
        targets = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
        with ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(self.vuln_scanner.scan_target, targets))
            self.assertEqual(len(results), len(targets))
    
    def test_report_generation(self):
        """Test report generation from scan results"""
        scan_results = self.vuln_scanner.scan_target("192.168.1.100")
        report = self.vuln_scanner.generate_report(scan_results)
        self.assertIn("summary", report)
        self.assertIn("recommendations", report)
        self.assertIn("details", report)

if __name__ == '__main__':
    unittest.main()
