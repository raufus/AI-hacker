"""
Scanning modules for various security assessments, including authenticated scans.

This module contains individual scanner classes that integrate with specific security tools.
Each scanner is designed to be called dynamically by the AutonomousAgent's scanning phase.
"""
import subprocess
import logging
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

# --- Base Class for Scanners ---
class BaseScanner:
    def __init__(self, tool_name: str):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.tool_name = tool_name

    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Each scanner must implement the 'scan' method.")

    def _is_command_available(self, command: str) -> bool:
        """Check if a command is available in the system's PATH."""
        return shutil.which(command) is not None

# --- Implemented Scanners ---
class VulnerabilityScanner(BaseScanner):
    """Integrates with Nikto and Nuclei for web server vulnerability scanning."""
    def __init__(self):
        super().__init__("Nikto+Nuclei")
        self.nikto_path = Path("tools/nikto/program/nikto.pl").resolve()
        self.nuclei_path = Path("tools/nuclei/nuclei.exe").resolve()

    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """Runs both Nikto and Nuclei scans, with optional authentication."""
        credentials = kwargs.get('credentials') # e.g., {'user': 'a', 'pass': 'b'} or {'cookie': '...'} 
        all_vulnerabilities = []
        
        nikto_results = self._run_nikto(target, credentials)
        if nikto_results.get('vulnerabilities'):
            all_vulnerabilities.extend(nikto_results['vulnerabilities'])

        nuclei_results = self._run_nuclei(target, credentials)
        if nuclei_results.get('vulnerabilities'):
            all_vulnerabilities.extend(nuclei_results['vulnerabilities'])

        self.logger.info(f"Combined scan for {target} found {len(all_vulnerabilities)} issues.")
        return {"vulnerabilities": all_vulnerabilities}

    def _run_nikto(self, target: str, creds: Optional[Dict] = None) -> Dict[str, Any]:
        if not self.nikto_path.exists(): return {"error": "Nikto not found"}
        self.logger.info(f"Running Nikto scan on {target}...")
        command = ["perl", str(self.nikto_path), "-h", target, "-Format", "json"]
        if creds and 'user' in creds and 'pass' in creds:
            self.logger.info("Using credentials for Nikto scan.")
            command.extend(["-id", f"{creds['user']}:{creds['pass']}"])
        
        try:
            # Nikto requires a file for output
            output_file = Path(f"nikto_results.json").resolve()
            command.extend(["-o", str(output_file)])
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=300)
            with open(output_file, 'r') as f: results = json.load(f)
            output_file.unlink()
            return {"vulnerabilities": results.get('vulnerabilities', [])}
        except Exception as e:
            return {"error": str(e)}

    def _run_nuclei(self, target: str, creds: Optional[Dict] = None) -> Dict[str, Any]:
        if not self.nuclei_path.exists(): return {"error": "Nuclei not found"}
        self.logger.info(f"Running Nuclei scan on {target}...")
        command = [str(self.nuclei_path), "-u", f"http://{target}", "-json"]
        if creds and 'cookie' in creds:
            self.logger.info("Using cookie for Nuclei scan.")
            command.extend(["-H", f"Cookie: {creds['cookie']}"])

        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=600)
            vulns = [json.loads(line) for line in result.stdout.strip().split('\n')]
            return {"vulnerabilities": vulns}
        except Exception as e:
            return {"error": str(e)}

class WebScanner(BaseScanner):
    """Integrates with SQLMap for SQL injection scanning."""
    def __init__(self):
        super().__init__("SQLMap")
        self.sqlmap_path = Path("tools/sqlmap/sqlmap.py").resolve()

    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        if not self.sqlmap_path.exists(): return {"error": "SQLMap not found"}
        credentials = kwargs.get('credentials') # e.g., {'cookie': '...'} 
        self.logger.info(f"Running SQLMap scan on {target}...")
        command = ["python", str(self.sqlmap_path), "-u", target, "--batch", "--level=1", "--risk=1"]
        if credentials and 'cookie' in credentials:
            self.logger.info("Using cookie for SQLMap scan.")
            command.append(f"--cookie=\"{credentials['cookie']}\"")

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            if "seems to be injectable" in result.stdout.lower():
                return {"vulnerabilities": [{"type": "SQLi", "details": result.stdout}]}
            return {"vulnerabilities": []}
        except subprocess.CalledProcessError as e:
            if "seems to be injectable" in e.stdout.lower():
                return {"vulnerabilities": [{"type": "SQLi", "details": e.stdout}]}
            return {"error": e.stderr}

class AuthScanner(BaseScanner):
    """Performs credential brute-forcing using Hydra."""
    def __init__(self):
        super().__init__("Hydra")
        if not self._is_command_available("hydra"):
            self.logger.error("Hydra is not installed or not in PATH. AuthScanner will not work.")

    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """Runs Hydra to find valid credentials."""
        service = kwargs.get('service')
        user_list = kwargs.get('user_list')
        pass_list = kwargs.get('pass_list')
        port = kwargs.get('port')

        if not all([service, user_list, pass_list]):
            return {"error": "Service, user_list, and pass_list are required for AuthScanner."}
        if not self._is_command_available("hydra"): 
            return {"error": "Hydra is not installed."}

        self.logger.info(f"Running Hydra scan on {target}:{port} for service {service}...")
        command = ["hydra", "-L", user_list, "-P", pass_list, target, service]
        if port:
            command.extend(["-s", str(port)])

        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=900)
            found_creds = []
            for line in result.stdout.splitlines():
                if "host:" in line and "login:" in line and "password:" in line:
                    found_creds.append(line.strip())
            
            if found_creds:
                self.logger.info(f"Hydra found {len(found_creds)} valid credentials.")
                return {"credentials_found": found_creds}
            else:
                self.logger.info("Hydra scan finished with no credentials found.")
                return {"credentials_found": []}
        except subprocess.TimeoutExpired:
            return {"error": "Hydra scan timed out after 15 minutes."}
        except subprocess.CalledProcessError as e:
            return {"error": f"Hydra failed: {e.stderr}"}

# --- Placeholder Scanners ---
class NetworkScanner(BaseScanner):
    """Placeholder for Nmap network scanning."""
    def __init__(self):
        super().__init__("Nmap")

    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        self.logger.warning("NetworkScanner is a placeholder.")
        return {"status": "skipped"}

class DirectoryBruteforcer(BaseScanner):
    """Placeholder for directory bruteforcing."""
    def __init__(self):
        super().__init__("Dirsearch")

    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        self.logger.warning("DirectoryBruteforcer is not implemented.")
        return {"status": "skipped"}

class CryptoScanner(BaseScanner):
    """Placeholder for SSL/TLS scanning."""
    def __init__(self):
        super().__init__("SSLyze")

    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        self.logger.warning("CryptoScanner is not implemented.")
        return {"status": "skipped"}
