import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .scanning_module import ScanningModule
import logging

class WebScanner(ScanningModule):
    """Web application scanner for finding common vulnerabilities."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'AI-HackerOS/1.0'})
        self.logger = logging.getLogger(__name__)

    @property
    def name(self) -> str:
        return "Web Scanner"

    def scan(self, target: str, options: dict = None):
        """Run a web scan on the given target URL."""
        if not target.startswith(('http://', 'https://')):
            target = 'http://' + target
        
        self.logger.info(f"Starting web scan on {target}")
        try:
            response = self.session.get(target, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Failed to connect to {target}: {e}")
            return {"error": f"Failed to connect to target: {e}"}

        soup = BeautifulSoup(response.text, 'html.parser')
        forms = self._find_forms(soup)
        links = self._find_links(soup, target)
        comments = self._find_comments(response.text)
        headers = dict(response.headers)

        results = {
            'url': target,
            'status_code': response.status_code,
            'forms': forms,
            'links': links,
            'comments': comments,
            'headers': headers,
            'vulnerabilities': []
        }

        results['vulnerabilities'].extend(self._check_security_headers(headers))
        results['vulnerabilities'].extend(self._check_forms(forms, target))

        return results

    def _find_forms(self, soup):
        return [form.prettify() for form in soup.find_all('form')]

    def _find_links(self, soup, base_url):
        links = []
        for a in soup.find_all('a', href=True):
            link = a['href']
            links.append(urljoin(base_url, link))
        return list(set(links))

    def _find_comments(self, text):
        from bs4 import Comment
        soup = BeautifulSoup(text, 'html.parser')
        return [comment.string.strip() for comment in soup.find_all(string=lambda text: isinstance(text, Comment))]

    def _check_security_headers(self, headers):
        vulnerabilities = []
        security_headers = {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-XSS-Protection': '1; mode=block',
            'X-Content-Type-Options': 'nosniff',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'"
        }
        for header, value in security_headers.items():
            if header not in headers:
                vulnerabilities.append({
                    'type': 'Missing Security Header',
                    'description': f"Missing security header: {header}. Recommended value: {value}"
                })
        return vulnerabilities

    def _check_forms(self, forms, url):
        vulnerabilities = []
        for form_html in forms:
            soup = BeautifulSoup(form_html, 'html.parser')
            form = soup.find('form')
            if form and form.get('method', '').lower() == 'post':
                # Simple check for CSRF tokens
                has_csrf_token = any(i.get('type') == 'hidden' and 'csrf' in i.get('name', '').lower() for i in form.find_all('input'))
                if not has_csrf_token:
                    vulnerabilities.append({
                        'type': 'Missing CSRF Token',
                        'description': f"Form on {url} appears to be missing a CSRF token.",
                        'form': str(form)
                    })
        return vulnerabilities
