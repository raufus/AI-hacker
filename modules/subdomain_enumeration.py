
"""
Subdomain enumeration module using multiple techniques
"""
import subprocess
import logging
import requests
import dns.resolver
from typing import List, Set
import threading
import time

class SubdomainEnumerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.subdomains = set()
        
    def run_sublist3r(self, domain: str) -> Set[str]:
        """Run Sublist3r for subdomain discovery"""
        try:
            result = subprocess.run([
                "sublist3r", "-d", domain, "-o", "/tmp/sublist3r_output.txt"
            ], capture_output=True, text=True, timeout=300)
            
            subdomains = set()
            if result.returncode == 0:
                with open("/tmp/sublist3r_output.txt", "r") as f:
                    for line in f:
                        subdomain = line.strip()
                        if subdomain and "." in subdomain:
                            subdomains.add(subdomain)
            
            return subdomains
        except Exception as e:
            self.logger.error(f"Sublist3r failed: {e}")
            return set()
    
    def run_assetfinder(self, domain: str) -> Set[str]:
        """Run assetfinder for subdomain discovery"""
        try:
            result = subprocess.run([
                "assetfinder", domain
            ], capture_output=True, text=True, timeout=300)
            
            subdomains = set()
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    subdomain = line.strip()
                    if subdomain and domain in subdomain:
                        subdomains.add(subdomain)
            
            return subdomains
        except Exception as e:
            self.logger.error(f"Assetfinder failed: {e}")
            return set()
    
    def bruteforce_subdomains(self, domain: str) -> Set[str]:
        """Bruteforce common subdomains"""
        common_subdomains = [
            "www", "mail", "ftp", "admin", "test", "dev", "staging", 
            "api", "blog", "shop", "support", "forum", "portal",
            "secure", "vpn", "remote", "login", "panel", "cpanel"
        ]
        
        subdomains = set()
        for sub in common_subdomains:
            subdomain = f"{sub}.{domain}"
            if self.check_subdomain_exists(subdomain):
                subdomains.add(subdomain)
                time.sleep(0.1)  # Rate limiting
        
        return subdomains
    
    def check_subdomain_exists(self, subdomain: str) -> bool:
        """Check if subdomain exists via DNS lookup"""
        try:
            dns.resolver.resolve(subdomain, 'A')
            return True
        except Exception:
            return False
    
    def comprehensive_enumeration(self, domain: str) -> List[str]:
        """Run comprehensive subdomain enumeration"""
        self.logger.info(f"Starting subdomain enumeration for {domain}")
        
        all_subdomains = set()
        
        # Run different tools in parallel
        methods = [
            self.run_sublist3r,
            self.run_assetfinder,
            self.bruteforce_subdomains
        ]
        
        threads = []
        results = {}
        
        def run_method(method, domain, results, index):
            results[index] = method(domain)
        
        for i, method in enumerate(methods):
            thread = threading.Thread(target=run_method, args=(method, domain, results, i))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join(timeout=600)  # 10 minute timeout
        
        # Combine results
        for result_set in results.values():
            all_subdomains.update(result_set)
        
        # Verify subdomains are alive
        alive_subdomains = []
        for subdomain in all_subdomains:
            try:
                response = requests.get(f"http://{subdomain}", timeout=5)
                if response.status_code < 400:
                    alive_subdomains.append(subdomain)
            except:
                try:
                    response = requests.get(f"https://{subdomain}", timeout=5)
                    if response.status_code < 400:
                        alive_subdomains.append(subdomain)
                except:
                    pass
        
        self.logger.info(f"Found {len(alive_subdomains)} live subdomains for {domain}")
        return alive_subdomains
