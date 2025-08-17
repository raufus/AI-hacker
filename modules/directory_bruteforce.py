
"""
Directory and file bruteforcing module
"""
import requests
import logging
import threading
from typing import List, Dict, Any
import time

class DirectoryBruteforcer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        
    def get_common_directories(self) -> List[str]:
        """Get list of common directories to test"""
        return [
            "admin", "administrator", "login", "panel", "control",
            "dashboard", "config", "backup", "test", "dev", "staging",
            "api", "wp-admin", "phpmyadmin", "cpanel", "webmail",
            "ftp", "ssh", "db", "database", "sql", "upload", "uploads",
            "images", "img", "css", "js", "assets", "static", "public",
            "private", "secret", "hidden", "temp", "tmp", "log", "logs",
            "cache", "backups", "old", "new", "beta", "alpha", "v1", "v2"
        ]
    
    def get_common_files(self) -> List[str]:
        """Get list of common files to test"""
        return [
            "robots.txt", "sitemap.xml", ".htaccess", "web.config",
            "config.php", "wp-config.php", "settings.php", "database.php",
            "db.php", "connect.php", "connection.php", "config.inc.php",
            "config.xml", "settings.xml", "web.xml", "applicationContext.xml",
            "login.php", "admin.php", "index.php", "home.php", "main.php",
            "readme.txt", "README.md", "changelog.txt", "version.txt",
            "backup.sql", "dump.sql", "database.sql", ".env", ".git/config",
            "phpinfo.php", "info.php", "test.php", "shell.php"
        ]
    
    def check_path(self, base_url: str, path: str) -> Dict[str, Any]:
        """Check if a path exists on the target"""
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        
        try:
            response = self.session.get(url, timeout=10, allow_redirects=False)
            
            return {
                "url": url,
                "status_code": response.status_code,
                "content_length": len(response.content),
                "content_type": response.headers.get('content-type', ''),
                "exists": response.status_code < 400
            }
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "exists": False
            }
    
    def bruteforce_directories(self, base_url: str, max_threads: int = 10) -> List[Dict[str, Any]]:
        """Bruteforce directories using threading"""
        directories = self.get_common_directories()
        files = self.get_common_files()
        all_paths = directories + files
        
        results = []
        results_lock = threading.Lock()
        
        def worker():
            while True:
                try:
                    path = path_queue.pop(0)
                except IndexError:
                    break
                
                result = self.check_path(base_url, path)
                
                with results_lock:
                    if result.get("exists"):
                        results.append(result)
                        self.logger.info(f"Found: {result['url']} ({result['status_code']})")
                
                time.sleep(0.1)  # Rate limiting
        
        # Create path queue
        path_queue = all_paths.copy()
        
        # Start threads
        threads = []
        for _ in range(min(max_threads, len(all_paths))):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def analyze_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze bruteforce results"""
        analysis = {
            "total_found": len(results),
            "by_status_code": {},
            "interesting_files": [],
            "admin_panels": [],
            "config_files": []
        }
        
        for result in results:
            status = result.get("status_code", 0)
            analysis["by_status_code"][status] = analysis["by_status_code"].get(status, 0) + 1
            
            url = result["url"].lower()
            
            # Categorize findings
            if any(term in url for term in ["admin", "panel", "login", "dashboard"]):
                analysis["admin_panels"].append(result)
            elif any(term in url for term in ["config", ".env", "web.config", ".htaccess"]):
                analysis["config_files"].append(result)
            elif any(ext in url for ext in [".sql", ".bak", ".old", ".txt"]):
                analysis["interesting_files"].append(result)
        
        return analysis
