
"""
Network utilities for IP validation, port scanning, etc.
"""
import socket
import ipaddress
import re
from typing import List, Dict, Any, Optional

class NetworkUtils:
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """Check if string is valid IP address"""
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        """Check if string is valid domain name"""
        pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        return bool(pattern.match(domain))
    
    @staticmethod
    def resolve_domain(domain: str) -> Optional[str]:
        """Resolve domain to IP address"""
        try:
            return socket.gethostbyname(domain)
        except socket.gaierror:
            return None
    
    @staticmethod
    def check_port_open(host: str, port: int, timeout: int = 3) -> bool:
        """Check if port is open on host"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    @staticmethod
    def scan_common_ports(host: str) -> List[int]:
        """Scan common ports on host"""
        common_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995, 1723, 3306, 3389, 5432, 5900, 8080
        ]
        
        open_ports = []
        for port in common_ports:
            if NetworkUtils.check_port_open(host, port):
                open_ports.append(port)
        
        return open_ports
    
    @staticmethod
    def get_service_banner(host: str, port: int, timeout: int = 3) -> Optional[str]:
        """Get service banner from port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            
            # Send HTTP request for web services
            if port in [80, 8080, 8000]:
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
            
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            return banner.strip()
        except Exception:
            return None
