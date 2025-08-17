
"""
Autonomous target discovery and selection module
"""
import ipaddress
import random
import logging
import subprocess
from typing import List, Dict, Any
import requests

class TargetDiscovery:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def discover_internal_networks(self) -> List[str]:
        """Discover internal network ranges"""
        internal_ranges = [
            "192.168.0.0/16",
            "10.0.0.0/8", 
            "172.16.0.0/12"
        ]
        
        active_networks = []
        for network in internal_ranges:
            if self.ping_network_gateway(network):
                active_networks.append(network)
                
        return active_networks
    
    def ping_network_gateway(self, network: str) -> bool:
        """Check if network gateway is reachable"""
        try:
            net = ipaddress.ip_network(network, strict=False)
            gateway = str(list(net.hosts())[0])  # First host as gateway
            
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", gateway],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def scan_network_range(self, network: str, max_hosts: int = 20) -> List[str]:
        """Scan network range for active hosts"""
        try:
            result = subprocess.run([
                "nmap", "-sn", "-T4", network
            ], capture_output=True, text=True, timeout=60)
            
            hosts = []
            for line in result.stdout.split('\n'):
                if 'Nmap scan report for' in line:
                    host = line.split()[-1].strip('()')
                    hosts.append(host)
                    if len(hosts) >= max_hosts:
                        break
                        
            return hosts
        except Exception as e:
            self.logger.error(f"Network scan failed: {e}")
            return []
    
    def select_high_value_targets(self, hosts: List[str]) -> List[Dict[str, Any]]:
        """Select high-value targets from host list"""
        targets = []
        
        for host in hosts:
            # Quick port scan to identify interesting services
            result = subprocess.run([
                "nmap", "-T4", "-F", host
            ], capture_output=True, text=True, timeout=30)
            
            open_ports = []
            for line in result.stdout.split('\n'):
                if '/tcp' in line and 'open' in line:
                    port = line.split('/')[0]
                    service = line.split()[-1] if len(line.split()) > 2 else 'unknown'
                    open_ports.append({"port": port, "service": service})
            
            if open_ports:
                priority = self.calculate_target_priority(open_ports)
                targets.append({
                    "host": host,
                    "ports": open_ports,
                    "priority": priority
                })
        
        # Sort by priority (higher is better)
        targets.sort(key=lambda x: x['priority'], reverse=True)
        return targets[:5]  # Return top 5 targets
    
    def calculate_target_priority(self, ports: List[Dict]) -> int:
        """Calculate target priority based on open services"""
        priority = 0
        high_value_ports = {
            "22": 10,   # SSH
            "80": 15,   # HTTP
            "443": 15,  # HTTPS
            "21": 8,    # FTP
            "23": 5,    # Telnet
            "3389": 12, # RDP
            "445": 10,  # SMB
            "3306": 8,  # MySQL
            "5432": 8,  # PostgreSQL
        }
        
        for port_info in ports:
            port = port_info["port"]
            if port in high_value_ports:
                priority += high_value_ports[port]
            else:
                priority += 1
                
        return priority
    
    def get_external_ip_ranges(self) -> List[str]:
        """Get external IP ranges (for educational purposes only)"""
        # This should only be used in authorized environments
        educational_ranges = [
            "scanme.nmap.org",
            "testphp.vulnweb.com",
            "demo.testfire.net"
        ]
        return educational_ranges
