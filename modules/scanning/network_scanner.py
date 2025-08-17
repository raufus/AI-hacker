import nmap
from .scanning_module import ScanningModule
import logging

class NetworkScanner(ScanningModule):
    """Network scanning module using nmap."""

    def __init__(self):
        self.scanner = nmap.PortScanner()
        self.logger = logging.getLogger(__name__)

    @property
    def name(self) -> str:
        return "Network Scanner"

    def scan(self, target: str, options: dict = None):
        """Run a network scan on the given target."""
        if options is None:
            options = {}
        
        ports = options.get('ports', '1-1024')
        arguments = options.get('arguments', '-sV -O')

        self.logger.info(f"Starting network scan on {target} for ports {ports} with arguments '{arguments}'")
        
        try:
            self.scanner.scan(target, ports, arguments)
            scan_results = []
            for host in self.scanner.all_hosts():
                host_info = {
                    'host': host,
                    'hostname': self.scanner[host].hostname(),
                    'state': self.scanner[host].state(),
                    'protocols': []
                }
                for proto in self.scanner[host].all_protocols():
                    proto_info = {'protocol': proto, 'ports': []}
                    lport = self.scanner[host][proto].keys()
                    for port in lport:
                        port_info = {
                            'port': port,
                            'state': self.scanner[host][proto][port]['state'],
                            'name': self.scanner[host][proto][port]['name'],
                            'product': self.scanner[host][proto][port]['product'],
                            'version': self.scanner[host][proto][port]['version'],
                            'extrainfo': self.scanner[host][proto][port]['extrainfo'],
                            'cpe': self.scanner[host][proto][port]['cpe']
                        }
                        proto_info['ports'].append(port_info)
                    host_info['protocols'].append(proto_info)
                scan_results.append(host_info)
            return scan_results
        except nmap.PortScannerError as e:
            self.logger.error(f"Nmap scan error for target {target}: {e}")
            return {"error": f"Nmap scan failed: {e}"}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during network scan for {target}: {e}")
            return {"error": f"An unexpected error occurred: {e}"}
