
"""
Browser automation module for web application testing
"""
import time
import logging
from typing import Dict, List, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class WebAutomation:
    def __init__(self, headless: bool = True):
        self.logger = logging.getLogger("WebAutomation")
        self.driver = None
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
        except Exception as e:
            self.logger.error(f"Failed to setup WebDriver: {e}")
    
    def navigate_to(self, url: str) -> bool:
        """Navigate to URL"""
        try:
            self.driver.get(url)
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def find_forms(self) -> List[Dict[str, Any]]:
        """Find all forms on the page"""
        forms = []
        try:
            form_elements = self.driver.find_elements(By.TAG_NAME, "form")
            for i, form in enumerate(form_elements):
                form_data = {
                    "id": i,
                    "action": form.get_attribute("action"),
                    "method": form.get_attribute("method"),
                    "inputs": []
                }
                
                inputs = form.find_elements(By.TAG_NAME, "input")
                for inp in inputs:
                    form_data["inputs"].append({
                        "name": inp.get_attribute("name"),
                        "type": inp.get_attribute("type"),
                        "value": inp.get_attribute("value")
                    })
                
                forms.append(form_data)
        except Exception as e:
            self.logger.error(f"Error finding forms: {e}")
        
        return forms
    
    def test_sql_injection(self, form_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test form for SQL injection vulnerabilities"""
        vulnerabilities = []
        sql_payloads = [
            "' OR '1'='1",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users--"
        ]
        
        for payload in sql_payloads:
            try:
                # Fill form with payload
                for inp in form_data["inputs"]:
                    if inp["type"] in ["text", "email", "password"]:
                        element = self.driver.find_element(By.NAME, inp["name"])
                        element.clear()
                        element.send_keys(payload)
                
                # Submit form
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                submit_btn.click()
                
                # Check for SQL error indicators
                page_source = self.driver.page_source.lower()
                error_indicators = ["sql", "mysql", "ora-", "postgresql", "error"]
                
                if any(indicator in page_source for indicator in error_indicators):
                    vulnerabilities.append({
                        "type": "SQL Injection",
                        "payload": payload,
                        "form_action": form_data["action"],
                        "severity": "High"
                    })
                
            except Exception as e:
                self.logger.debug(f"Error testing payload {payload}: {e}")
        
        return vulnerabilities
    
    def test_xss(self, form_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Test form for XSS vulnerabilities"""
        vulnerabilities = []
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            try:
                # Fill form with payload
                for inp in form_data["inputs"]:
                    if inp["type"] in ["text", "email"]:
                        element = self.driver.find_element(By.NAME, inp["name"])
                        element.clear()
                        element.send_keys(payload)
                
                # Submit form
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                submit_btn.click()
                
                # Check if payload is reflected
                if payload in self.driver.page_source:
                    vulnerabilities.append({
                        "type": "Cross-Site Scripting (XSS)",
                        "payload": payload,
                        "form_action": form_data["action"],
                        "severity": "Medium"
                    })
                
            except Exception as e:
                self.logger.debug(f"Error testing XSS payload {payload}: {e}")
        
        return vulnerabilities
    
    def scan_website(self, url: str) -> Dict[str, Any]:
        """Comprehensive website scan"""
        results = {
            "url": url,
            "forms": [],
            "vulnerabilities": [],
            "technologies": [],
            "links": []
        }
        
        if not self.navigate_to(url):
            return results
        
        # Find forms
        forms = self.find_forms()
        results["forms"] = forms
        
        # Test each form
        for form in forms:
            # Test SQL injection
            sql_vulns = self.test_sql_injection(form)
            results["vulnerabilities"].extend(sql_vulns)
            
            # Test XSS
            xss_vulns = self.test_xss(form)
            results["vulnerabilities"].extend(xss_vulns)
        
        # Find all links
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            results["links"] = [link.get_attribute("href") for link in links if link.get_attribute("href")]
        except Exception as e:
            self.logger.error(f"Error finding links: {e}")
        
        return results
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
