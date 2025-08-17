
"""
AI decision engine for cybersecurity operations
"""
import json
from typing import Dict, List, Any
from .llm import LLMEngine

class AIPlanner:
    def __init__(self, llm_engine: LLMEngine):
        self.llm = llm_engine
        self.current_phase = "reconnaissance"
        self.target_data = {}
    
    def analyze_target(self, target: str) -> Dict[str, Any]:
        """Analyze target and create initial assessment"""
        assessment = {
            "target": target,
            "ip_range": None,
            "domain": None,
            "technologies": [],
            "vulnerabilities": [],
            "attack_vectors": []
        }
        return assessment
    
    def plan_next_action(self, current_results: Dict[str, Any]) -> Dict[str, str]:
        """Decide next action based on current results"""
        prompt = f"Based on current results: {json.dumps(current_results)}, what should be the next action?"
        response = self.llm.query(prompt)
        
        return {
            "action": "scan_ports",
            "tool": "nmap",
            "parameters": {},
            "reasoning": response
        }
    
    def evaluate_results(self, results: Dict[str, Any]) -> bool:
        """Evaluate if results meet objectives"""
        return len(results.get("findings", [])) > 0

    def analyze_recon_data(self, recon_findings: Dict[str, Any]) -> str:
        """Analyze reconnaissance findings and provide a high-level summary."""
        prompt = f"""
        As a senior penetration tester, analyze the following reconnaissance data.
        Provide a brief, high-level summary of the target's attack surface.
        Focus on the most promising avenues for attack.

        Reconnaissance Data:
        {json.dumps(recon_findings, indent=2)}

        Summary:
        """
        summary = self.llm.query(prompt)
        return summary

    def generate_scan_plan(self, recon_findings: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a detailed, strategic plan for the scanning phase based on recon data."""
        prompt = f"""
        As a professional penetration tester, create a strategic scanning plan based on the reconnaissance data provided.
        Your plan should be a JSON object detailing which scanners to use for each target and why.

        Available Scanners:
        - 'network_scanner': For port scanning and service version detection (Nmap).
        - 'web_scanner': For identifying web vulnerabilities (e.g., XSS, SQLi) on web applications.
        - 'vulnerability_scanner': For checking for known CVEs based on service versions.
        - 'dir_bruteforcer': For discovering hidden directories and files on web servers.
        - 'crypto_scanner': For checking for weak SSL/TLS configurations.
        - 'auth_scanner': For testing for weak credentials on login pages.

        Reconnaissance Data:
        {json.dumps(recon_findings, indent=2)}

        Instructions:
        - For each discovered target (including subdomains), create a plan.
        - Prioritize scans based on the technologies identified (e.g., if a web server is found, prioritize web-related scans).
        - Provide a clear 'reasoning' for each planned scan.
        - Format the output as a single JSON object.

        Example Output:
        {{
            "scan_plan": [
                {{
                    "target": "example.com",
                    "scanners": [
                        {{
                            "module": "web_scanner",
                            "reasoning": "A web server was identified. Scanning for common web vulnerabilities is the next logical step."
                        }},
                        {{
                            "module": "dir_bruteforcer",
                            "reasoning": "The web server may have hidden administrative panels or sensitive files."
                        }}
                    ]
                }},
                {{
                    "target": "api.example.com",
                    "scanners": [
                        {{
                            "module": "auth_scanner",
                            "reasoning": "The 'api' subdomain suggests a potential authentication endpoint that should be tested for weak credentials."
                        }}
                    ]
                }}
            ]
        }}

        JSON Plan:
        """
        plan_str = self.llm.query(prompt)
        try:
            # Clean the response to extract only the JSON part
            cleaned_plan_str = self._extract_json_from_response(plan_str)
            return json.loads(cleaned_plan_str)
        except json.JSONDecodeError:
            self.llm.logger.error(f"Failed to decode JSON from LLM scan plan: {plan_str}")
            return {"error": "Failed to generate a valid JSON scan plan."}

    def _extract_json_from_response(self, response: str) -> str:
        """Extracts a JSON object from a string, cleaning up markdown code blocks."""
        # Find the start of the JSON markdown block
        json_block_start = response.find('```json')
        if json_block_start != -1:
            response = response[json_block_start + len('```json'):]

        # Find the start of the JSON object
        start_brace = response.find('{')
        # Find the end of the JSON object
        end_brace = response.rfind('}')

        if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
            return response[start_brace:end_brace + 1].strip()
        
        # Fallback for cases where there's no markdown but just the JSON
        return response.strip()

    def generate_exploitation_plan(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a strategic exploitation plan based on a list of vulnerabilities."""
        prompt = f"""
        As a master penetration tester, create a strategic exploitation plan for the following vulnerabilities.
        Your primary tool is Metasploit. For each vulnerability, suggest a specific Metasploit exploit module to use.
        Provide the plan as a JSON object.

        Discovered Vulnerabilities:
        {json.dumps(vulnerabilities, indent=2)}

        Instructions:
        - Analyze each vulnerability to determine if it is likely exploitable.
        - For exploitable vulnerabilities, recommend a specific, full Metasploit exploit module name (e.g., 'exploit/windows/smb/ms17_010_eternalblue').
        - Include any necessary options for the exploit (e.g., 'RPORT').
        - Provide clear reasoning for your choice.
        - If no suitable exploit is obvious, state that and suggest manual investigation.

        Example Output:
        {{
            "exploitation_plan": [
                {{
                    "vulnerability": {{ "type": "SQLi", "target": "http://example.com/login.php" }},
                    "action": "exploit",
                    "module": "exploit/multi/http/sqlmap_sql_injection",
                    "options": {{ "RHOSTS": "example.com", "PATH": "/login.php" }},
                    "reasoning": "The SQLMap scan confirmed a SQL injection vulnerability, which can be further exploited using the dedicated SQLMap module in Metasploit to gain a shell."
                }},
                {{
                    "vulnerability": {{ "type": "outdated_apache", "target": "10.0.0.5" }},
                    "action": "investigate",
                    "reasoning": "The Apache version is old, but no direct, reliable remote code execution exploit is available in Metasploit. This requires manual investigation."
                }}
            ]
        }}

        JSON Plan:
        """
        plan_str = self.llm.query(prompt)
        try:
            cleaned_plan_str = self._extract_json_from_response(plan_str)
            return json.loads(cleaned_plan_str)
        except json.JSONDecodeError:
            self.llm.logger.error(f"Failed to decode JSON from LLM exploitation plan: {plan_str}")
            return {"error": "Failed to generate a valid JSON exploitation plan."}
