
"""
Reconnaissance module - Nmap, Sublist3r, Whatweb scanning
"""
import subprocess
import json
import logging
import platform
import os
from pathlib import Path
from typing import Dict, List, Any

from utils.logger import setup_logger

class ReconModule:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.tools = ["nmap", "sublist3r", "whatweb"]
    
    def nmap_scan(self, target: str) -> Dict[str, Any]:
        """
        Perform an intelligent, multi-stage Nmap scan to identify live hosts,
        open ports, and service versions.
        """
        # On Windows, Nmap might not be in PATH, so check default location
        nmap_path = 'nmap'
        if platform.system() == "Windows":
            if os.path.exists(r"C:\Program Files (x86)\Nmap\nmap.exe"):
                nmap_path = r"C:\Program Files (x86)\Nmap\nmap.exe"
            elif not self._is_nmap_installed():
                self.logger.error("Nmap is not installed or not in PATH. Skipping Nmap scan.")
                return {"error": "Nmap not installed."}
        elif not self._is_nmap_installed():
            self.logger.error("Nmap is not installed or not in PATH. Skipping Nmap scan.")
            return {"error": "Nmap not installed."}

        try:
            # 1. Fast scan for top ports to quickly find open ones
            self.logger.info(f"[{target}] Performing fast scan on top ports...")
            fast_scan_cmd = [nmap_path, "-F", "--open", target, "-oX", "-"]
            scan_result = subprocess.run(fast_scan_cmd, capture_output=True, text=True, check=True)

            open_ports = self._parse_nmap_xml(scan_result.stdout)

            if not open_ports:
                self.logger.info(f"[{target}] No open ports found in initial fast scan.")
                return {"target": target, "status": "up", "ports": []}

            self.logger.info(f"[{target}] Found open ports: {', '.join(map(str, open_ports))}. Performing detailed scan...")

            # 2. Detailed scan on discovered ports for service versions and OS
            ports_str = ",".join(map(str, open_ports))
            detailed_scan_cmd = [nmap_path, "-sV", "-O", "-p", ports_str, target, "-oX", "-"]
            detailed_result = subprocess.run(detailed_scan_cmd, capture_output=True, text=True, check=True)

            return self._parse_nmap_xml(detailed_result.stdout, detailed=True)

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"[{target}] An error occurred during Nmap scan: {e}")
            if hasattr(e, 'stderr') and e.stderr:
                self.logger.error(f"Nmap stderr: {e.stderr.strip()}")
            return {"error": str(e), "target": target, "ports": []}
        except Exception as e:
            self.logger.error(f"[{target}] An unexpected error occurred while parsing Nmap output: {e}")
            return {"error": "Failed to parse Nmap output.", "target": target, "ports": []}
    
    def subdomain_enum(self, domain: str) -> List[str]:
        """Enumerate subdomains using Sublist3r"""
        sublist3r_path = Path("tools/sublist3r/sublist3r.py").resolve()
        output_file = Path(f"subdomains_{domain}.txt").resolve()

        if not sublist3r_path.exists():
            self.logger.error(f"Sublist3r not found at {sublist3r_path}")
            return []

        try:
            self.logger.info(f"Running Sublist3r on {domain}...")
            command = [
                "python", str(sublist3r_path),
                "-d", domain,
                "-o", str(output_file)
            ]
            subprocess.run(command, check=True, capture_output=True, text=True)

            if output_file.exists():
                with open(output_file, 'r') as f:
                    subdomains = [line.strip() for line in f.readlines()]
                self.logger.info(f"Found {len(subdomains)} subdomains.")
                output_file.unlink()  # Clean up the file
                return subdomains
            return []
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"Error running Sublist3r: {e}")
            if hasattr(e, 'stderr') and e.stderr:
                self.logger.error(f"Sublist3r stderr: {e.stderr}")
            return []
    
    def web_tech_scan(self, url: str) -> Dict[str, Any]:
        """Scan web technologies using Whatweb."""
        whatweb_path = Path("tools/whatweb/whatweb").resolve()

        if not self._is_ruby_installed():
            self.logger.error("Ruby is not installed. Cannot run WhatWeb.")
            return {"error": "Ruby not installed."}

        if not whatweb_path.exists():
            self.logger.error(f"WhatWeb not found at {whatweb_path}")
            return {"error": "WhatWeb not found."}

        output_file = Path(f"whatweb_{url.replace('/', '_')}.json").resolve()
        try:
            self.logger.info(f"Running WhatWeb on {url}...")
            command = [
                'bundle', 'exec', 'ruby', str(whatweb_path), f'--log-json={output_file}', url
            ]
            # The cwd should be the whatweb directory for bundle to work
            cwd = os.path.dirname(whatweb_path)
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', cwd=cwd)

            if output_file.exists():
                with open(output_file, 'r') as f:
                    # WhatWeb logs one JSON object per line
                    results = [json.loads(line) for line in f]
                self.logger.info(f"WhatWeb scan complete. Found {len(results)} results.")
                output_file.unlink() # Clean up
                return results[0] if results else {}
            return {}
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"Error running WhatWeb: {e}")
            if hasattr(e, 'stderr') and e.stderr:
                self.logger.error(f"WhatWeb stderr: {e.stderr}")
            return {"error": str(e)}

    def _is_ruby_installed(self) -> bool:
        """Check if Ruby is installed and available in the system's PATH."""
        try:
            subprocess.run(["ruby", "-v"], check=True, capture_output=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _is_nmap_installed(self) -> bool:
        """Check if Nmap is installed and available in the system's PATH."""
        try:
            subprocess.run(["nmap", "--version"], check=True, capture_output=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _parse_nmap_xml(self, xml_output: str, detailed: bool = False) -> Dict[str, Any]:
        """Parse Nmap XML output to extract port and service information."""
        import xml.etree.ElementTree as ET
        results = {"ports": [], "os": "Unknown", "services": {}}
        try:
            root = ET.fromstring(xml_output)
            host_element = root.find('host')
            if host_element is None:
                return results if detailed else []

            ports_element = host_element.find('ports')
            if ports_element:
                for port_element in ports_element.findall('port'):
                    port_id = int(port_element.get('portid'))
                    state_element = port_element.find('state')
                    if state_element is not None and state_element.get('state') == 'open':
                        if not detailed:
                            results['ports'].append(port_id)
                            continue
                        
                        results['ports'].append(port_id)
                        service_element = port_element.find('service')
                        if service_element is not None:
                            service_info = {
                                'name': service_element.get('name', 'unknown'),
                                'product': service_element.get('product', ''),
                                'version': service_element.get('version', '')
                            }
                            results['services'][port_id] = service_info

            if detailed:
                os_element = host_element.find('os')
                if os_element:
                    osmatch_element = os_element.find('osmatch')
                    if osmatch_element is not None:
                        results['os'] = osmatch_element.get('name', 'Unknown')
                return results

            return results['ports']

        except ET.ParseError as e:
            logging.getLogger(__name__).error(f"Failed to parse Nmap XML: {e}")
            return results if detailed else []
