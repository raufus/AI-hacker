import requests
from .scanning_module import ScanningModule
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

class DirectoryBruteforcer(ScanningModule):
    """A simple directory and file bruteforcer."""

    def __init__(self, wordlist_path='wordlists/common.txt'):
        self.wordlist_path = wordlist_path
        self.logger = logging.getLogger(__name__)
        try:
            with open(self.wordlist_path, 'r') as f:
                self.wordlist = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            self.logger.warning(f"Wordlist not found at {self.wordlist_path}. Using a default small list.")
            self.wordlist = ['admin', 'test', 'backup', 'dev', 'api', 'config', 'wp-admin', 'robots.txt']

    @property
    def name(self) -> str:
        return "Directory Bruteforcer"

    def scan(self, target: str, options: dict = None):
        """Performs directory and file bruteforcing."""
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target
        if not target.endswith('/'):
            target += '/'

        self.logger.info(f"Starting directory bruteforce on {target}")
        
        found_paths = []
        max_workers = options.get('max_workers', 10) if options else 10

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self._check_path, target, path): path for path in self.wordlist}
            for future in as_completed(future_to_url):
                result = future.result()
                if result:
                    found_paths.append(result)
                    self.logger.info(f"Found: {result['url']} (Status: {result['status_code']})")

        self.logger.info(f"Directory bruteforce finished. Found {len(found_paths)} paths.")
        return {'found_paths': found_paths}

    def _check_path(self, base_url, path):
        url = f"{base_url}{path}"
        try:
            response = requests.get(url, timeout=5, allow_redirects=False)
            if 200 <= response.status_code < 400:
                return {'url': url, 'status_code': response.status_code}
        except requests.RequestException:
            pass
        return None
