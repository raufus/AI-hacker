
"""
Autonomous hacking logic & orchestration
"""
import time
import logging
from typing import Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_brain.llm import LLMEngine
from ai_brain.planner import AIPlanner
from modules.reconnaissance import ReconModule
from modules.scanning import VulnerabilityScanner, AuthScanner
from modules.exploitation import ExploitationModule
from modules.post_exploitation import PostExploitationModule
from modules.automation import BrowserAutomation
from config.config_manager import ConfigManager
from utils.logger import setup_logger

class AutonomousAgent:
    def __init__(self, target: str):
        self.target = target
        self.logger = setup_logger("AutonomousAgent")
        
        # Initialize AI components
        self.config = ConfigManager()
        self.llm_engine = LLMEngine()
        self.planner = AIPlanner(self.llm_engine)
        
        # Initialize modules
        self.recon = ReconModule()
        self.vuln_scanner = VulnerabilityScanner() # Consolidates multiple scanners
        self.auth_scanner = AuthScanner()
        self.exploiter = ExploitationModule(msf_password=self.config.get_setting('metasploit.password'))
        self.browser = BrowserAutomation()
        
        # State management
        self.current_phase = "reconnaissance"
        self.findings = {}
        self.vulnerabilities = []
        self.active_sessions = []
        self._start_time = time.time()
    
    def run_autonomous_operation(self):
        """Main autonomous operation loop"""
        self.logger.info(f"Starting autonomous operation against {self.target}")
        
        # --- Phase 1: Reconnaissance ---
        self.current_phase = "reconnaissance"
        self.logger.info("Entering reconnaissance phase")
        self._reconnaissance_phase()
        if not self.findings.get('scan_plan'):
            self.logger.warning("No scan plan generated from reconnaissance. Halting operation.")
            return

        # --- Phase 2: Scanning ---
        self.current_phase = "scanning"
        self.logger.info("Entering scanning phase")
        self._scanning_phase()
        if not self._should_continue_to_next_phase():
            self.logger.info("AI decision to halt after scanning phase.")
            return

        # --- Phase 3: Exploitation ---
        self.current_phase = "exploitation"
        self.logger.info("Entering exploitation phase")
        self._exploitation_phase()
        if not self._should_continue_to_next_phase():
            self.logger.info("AI decision to halt after exploitation phase.")
            return

        # --- Phase 4: Post-Exploitation ---
        self.current_phase = "post_exploitation"
        self.logger.info("Entering post-exploitation phase")
        self._post_exploitation_phase()

        self.logger.info("Autonomous operation complete.")
    
    def _reconnaissance_phase(self):
        """Reconnaissance phase operations with dynamic target expansion and AI planning."""
        self.logger.info("Starting reconnaissance phase...")
        initial_targets = [self.target]

        # --- Subdomain Enumeration ---
        if "." in self.target and not self.target.replace(".", "").isdigit():
            self.logger.info(f"Enumerating subdomains for {self.target}")
            subdomains = self.recon.subdomain_enum(self.target)
            if subdomains:
                self.logger.info(f"Discovered {len(subdomains)} subdomains. Adding to target list.")
                self.findings['subdomains'] = subdomains
                initial_targets.extend(subdomains)
        
        # --- Technology Fingerprinting & Port Scanning for all targets ---
        # Filter out any empty or invalid targets before scanning
        valid_targets = {t for t in initial_targets if t and t.strip()}
        for target in valid_targets:
            self.logger.info(f"Running reconnaissance on {target}")
            
            # Web technology scanning
            http_url = f"http://{target}"
            web_tech = self.recon.web_tech_scan(http_url)
            if web_tech and not web_tech.get('error'):
                self.findings.setdefault(target, {})['web_tech'] = web_tech
                self.logger.info(f"Identified web technologies for {target}: {web_tech.get('plugins', {}).keys()}")

            # Basic Nmap scan
            nmap_results = self.recon.nmap_scan(target)
            if nmap_results and not nmap_results.get('error'):
                self.findings.setdefault(target, {})['nmap'] = nmap_results
                self.logger.info(f"Nmap scan for {target} complete. Found {len(nmap_results.get('ports', []))} open ports.")

        # --- AI-Powered Analysis and Planning ---
        self.logger.info("Analyzing reconnaissance findings with AI...")
        recon_summary = self.planner.analyze_recon_data(self.findings)
        self.logger.info(f"AI Recon Analysis: {recon_summary}")

        # Generate a high-level plan for the scanning phase
        self.scan_plan = self.planner.generate_scan_plan(self.findings)
        self.logger.info(f"AI-generated scan plan: {self.scan_plan}")

        self.logger.info(f"Reconnaissance phase complete. Total findings: {len(self.findings)}")
    
    def _scanning_phase(self):
        """Executes the AI-generated scan plan from the reconnaissance phase."""
        self.logger.info("Starting AI-driven vulnerability scanning phase...")

        if not hasattr(self, 'scan_plan') or not self.scan_plan.get('scan_plan'):
            self.logger.warning("No scan plan generated. Skipping scanning phase.")
            return

        self.logger.info(f"Executing scan plan: {json.dumps(self.scan_plan, indent=2)}")

        scanner_map = {
            'network_scanner': self.network_scanner,
            'web_scanner': self.web_scanner,
            'vulnerability_scanner': self.vuln_scanner,
            'dir_bruteforcer': self.dir_bruteforcer,
            'crypto_scanner': self.crypto_scanner,
            'auth_scanner': self.auth_scanner
        }

        for plan_item in self.scan_plan.get('scan_plan', []):
            target = plan_item.get('target')
            scanners_to_run = plan_item.get('scanners', [])

            if not target:
                continue

            self.logger.info(f"--- Executing scans for target: {target} ---")

            for scanner_info in scanners_to_run:
                module_name = scanner_info.get('module')
                reasoning = scanner_info.get('reasoning', 'No reasoning provided.')
                scanner_instance = scanner_map.get(module_name)

                if scanner_instance:
                    self.logger.info(f"Running {module_name} on {target}. Reason: {reasoning}")
                    try:
                        # Assuming each scanner has a `scan` method
                        scan_results = scanner_instance.scan(target)
                        self.findings.setdefault(target, {}).setdefault('scans', {})[module_name] = scan_results
                        if scan_results and not scan_results.get('error'):
                            self.logger.info(f"{module_name} completed successfully.")
                            # Collect vulnerabilities if the scanner finds them
                            if 'vulnerabilities' in scan_results:
                                self.vulnerabilities.extend(scan_results['vulnerabilities'])
                        else:
                            self.logger.warning(f"{module_name} returned an error or no results.")
                    except Exception as e:
                        self.logger.error(f"An error occurred while running {module_name} on {target}: {e}")
                else:
                    self.logger.warning(f"Scanner module '{module_name}' not found.")
        
        self.logger.info(f"AI-driven scanning phase complete. Total vulnerabilities found: {len(self.vulnerabilities)}")
    
    def _exploitation_phase(self):
        """Executes an AI-generated exploitation plan based on discovered vulnerabilities."""
        self.logger.info("Starting exploitation phase...")

        if not self.findings.get('vulnerabilities'):
            self.logger.info("No vulnerabilities found to exploit.")
            return

        # For now, we'll try to exploit the first vulnerability found.
        # The AI planner can be enhanced later to choose the best one.
        vuln = self.findings['vulnerabilities'][0]
        target_host = vuln.get('host', self.target)
        target_port = vuln.get('port')
        exploit_query = vuln.get('name', '') # e.g., 'vsftpd 2.3.4'

        if not all([target_host, target_port, exploit_query]):
            self.logger.error(f"Vulnerability information is incomplete. Cannot exploit. {vuln}")
            return

        self.logger.info(f"Attempting to exploit '{exploit_query}' on {target_host}:{target_port}")
        self.exploiter.run(target_host, target_port, exploit_query)

        if self.exploiter.active_session:
            self.logger.success("Exploitation successful! Active session stored.")
            self.active_sessions.append(self.exploiter.active_session)
        else:
            self.logger.warning("Exploitation attempt finished, but no active session was created.")

        self.logger.info("Exploitation phase complete.")
    
    def _post_exploitation_phase(self):
        """Runs post-exploitation commands on any active sessions."""
        self.logger.info("Starting post-exploitation phase...")

        if not self.active_sessions:
            self.logger.info("No active sessions to perform post-exploitation on.")
            return

        for session in self.active_sessions:
            self.logger.info(f"Running post-exploitation on session {session.sid}")
            try:
                post_exploit_module = PostExploitationModule(session)
                enum_results = post_exploit_module.run_enumeration()

                if 'post_exploitation' not in self.findings:
                    self.findings['post_exploitation'] = []
                self.findings['post_exploitation'].append(enum_results)

                self.logger.success(f"Post-exploitation enumeration complete for session {session.sid}.")
                self.logger.info(f"Results: {enum_results}")

            except Exception as e:
                self.logger.error(f"Failed to run post-exploitation on session {session.sid}: {e}")
                self.logger.error(f"Post-exploitation for session {session_id} failed: {post_exploit_results.get('error')}")

        self.logger.info("Post-exploitation phase complete.")
    
    def _should_continue_to_next_phase(self) -> bool:
        """AI-powered decision on phase progression with advanced criteria"""
        # Get current state metrics
        current_state = {
            "phase": self.current_phase,
            "findings": len(self.findings),
            "vulnerabilities": len(self.vulnerabilities),
            "active_sessions": len(self.active_sessions),
            "target_type": self._determine_target_type(),
            "resource_usage": self._get_system_resources(),
            "time_elapsed": self._get_time_elapsed()
        }
        
        # Get AI recommendation
        next_action = self.planner.plan_next_action(current_state)
        
        # Advanced decision logic for continuing *after* scanning
        if self.current_phase == "scanning":
            # Continue to exploitation if we found exploitable vulnerabilities
            if self.vulnerabilities and self._are_vulns_exploitable():
                self.logger.info("Found exploitable vulnerabilities. Proceeding to exploitation.")
                return True
            
        elif self.current_phase == "exploitation":
            # Continue to post-exploitation if we have active sessions
            if self.active_sessions:
                self.logger.info("Active sessions established. Proceeding to post-exploitation.")
                return True
            
        # Check resource constraints
        if not self._check_resource_limits():
            return False
            
        return next_action == "continue"
    
    def _determine_target_type(self) -> str:
        """Determine target type based on findings"""
        if "web_tech" in self.findings:
            tech = self.findings["web_tech"]
            if "CMS" in tech:
                return "web_cms"
            elif "framework" in tech:
                return "web_framework"
            return "web_server"
        return "unknown"
    
    def _get_system_resources(self) -> Dict[str, float]:
        """Get current system resource usage"""
        import psutil
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
    
    def _get_time_elapsed(self) -> float:
        """Get time elapsed since operation start"""
        if hasattr(self, '_start_time'):
            return time.time() - self._start_time
        return 0
    
    def _has_critical_findings(self) -> bool:
        """Check for critical findings"""
        if "web_vulnerabilities" in self.findings:
            for vuln in self.findings["web_vulnerabilities"]:
                if vuln.get("severity", "low") == "critical":
                    return True
        return False
    
    def _are_vulns_exploitable(self) -> bool:
        """Check if found vulnerabilities are exploitable"""
        for vuln in self.vulnerabilities:
            if vuln.get("exploitability", "low") in ["high", "critical"]:
                return True
        return False
    
    def _has_high_value_target(self) -> bool:
        """Check if current target is high value"""
        if "subdomains" in self.findings:
            for sub in self.findings["subdomains"]:
                if "admin" in sub or "api" in sub:
                    return True
        return False
    
    def _check_resource_limits(self) -> bool:
        """Check if system resources are within limits"""
        resources = self._get_system_resources()
        for key, value in resources.items():
            if value > 80:  # 80% resource usage threshold
                return False
        return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python main_agent.py <target>")
        sys.exit(1)
    
    target = sys.argv[1]
    agent = AutonomousAgent(target)
    agent.run_autonomous_operation()

if __name__ == "__main__":
    main()
