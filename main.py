
#!/usr/bin/env python3
"""
AI_HackerOS - Educational Cybersecurity Research Platform
Main entry point for the autonomous penetration testing system
"""

import sys
import os
import argparse
import logging
from typing import Optional
import time

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logger, SecurityLogger
from agent.main_agent import AutonomousAgent
from modules.burp_launcher import BurpLauncher
from modules.installer import ToolsInstaller
from modules.target_discovery import TargetDiscovery
from report.reporter import SecurityReporter
from config.settings import config

def print_banner():
    """Print ASCII banner"""
    banner = """
    +------------------------------------------+
    |              AI_HackerOS                 |
    |    Educational Cybersecurity Platform    |
    |                                          |
    |   (WARNING) FOR AUTHORIZED TESTING ONLY  |
    +------------------------------------------+
    """
    print(banner)

def check_prerequisites(skip_checks: bool = False):
    """Check for and install missing system tools and Python packages."""
    logger = setup_logger("Prerequisites")
    if skip_checks:
        logger.info("Skipping prerequisite checks.")
        return

    logger.info("Checking and installing prerequisites...")
    installer = ToolsInstaller()
    
    installer.ensure_all_tools_installed()

def discover_targets() -> list:
    """Discover targets autonomously"""
    logger = setup_logger("TargetDiscovery")
    discovery = TargetDiscovery()
    
    logger.info("Starting autonomous target discovery...")
    
    # Discover internal networks
    internal_networks = discovery.discover_internal_networks()
    logger.info(f"Found internal networks: {internal_networks}")
    
    all_targets = []
    for network in internal_networks:
        hosts = discovery.scan_network_range(network)
        targets = discovery.select_high_value_targets(hosts)
        all_targets.extend(targets)
    
    # Add educational external targets
    external_targets = discovery.get_external_ip_ranges()
    for target in external_targets:
        all_targets.append({"host": target, "priority": 5, "ports": []})
    
    logger.info(f"Discovered {len(all_targets)} potential targets")
    return all_targets

def run_autonomous_mode(target: str):
    """Run autonomous penetration testing"""
    logger = setup_logger("AutonomousMode")
    security_logger = SecurityLogger(logger)
    
    # Auto-discover targets if specified
    if target == "auto-discover":
        logger.info("Starting autonomous target discovery...")
        targets = discover_targets()
        if not targets:
            logger.warning("No targets discovered")
            return
        
        # Select highest priority target
        target = targets[0]["host"]
        logger.info(f"Selected target: {target}")
    
    logger.info(f"Starting autonomous operation against: {target}")
    
    # Log the operation start and display a warning
    logger.info(f"Starting autonomous operation against: {target}")
    print(f"\n⚠️  WARNING: Autonomous penetration testing initiated against: {target}")
    print("This should ONLY be used against systems you own or have explicit permission to test.")
    
    # Log the start of operation
    security_logger.log_security_event(
        "AUTONOMOUS_TEST_START",
        target,
        {"mode": "autonomous", "authorized": True}
    )

    try:
        # Create an agent instance with the specified target
        agent = AutonomousAgent(target=target)

        # Run the agent's autonomous lifecycle
        agent.run_autonomous_operation()

        # Generate report from agent's findings
        logger.info("Autonomous operation complete. Generating security report...")
        reporter = SecurityReporter(output_dir="reports")
        reporter.set_target(target)

        if agent.findings.get('reconnaissance'):
            reporter.add_reconnaissance_data(agent.findings['reconnaissance'])
        
        if agent.findings.get('vulnerabilities'):
            for vuln in agent.findings['vulnerabilities']:
                reporter.add_vulnerability(vuln)

        if agent.findings.get('post_exploitation'):
            for result in agent.findings['post_exploitation']:
                reporter.add_exploitation_result(result)

        # Generate all report formats
        md_path = reporter.generate_markdown_report()
        html_path = reporter.generate_html_report()
        json_path = reporter.generate_json_report()

        logger.info(f"Markdown report generated: {md_path}")
        logger.info(f"HTML report generated: {html_path}")
        logger.info(f"JSON report generated: {json_path}")

    except Exception as e:
        logger.critical(f"A critical error occurred during autonomous operation: {e}", exc_info=True)
        security_logger.log_security_event(
            "AUTONOMOUS_TEST_ERROR",
            target,
            {"error": str(e)}
        )

def run_continuous_mode():
    """Run in continuous autonomous mode"""
    logger = setup_logger("ContinuousMode")
    
    logger.info("Starting continuous autonomous mode...")
    
    while True:
        try:
            # Discover new targets
            targets = discover_targets()
            
            for target_info in targets[:3]:  # Test top 3 targets
                target = target_info["host"]
                logger.info(f"Testing target: {target} (Priority: {target_info['priority']})")
                
                # Run autonomous test
                run_autonomous_mode(target)
                
                # Wait before next target
                import time
                time.sleep(300)  # 5 minutes between targets
                
            # Wait before next discovery cycle
            logger.info("Cycle complete. Waiting 1 hour before next cycle...")
            time.sleep(3600)  # 1 hour between cycles
            
        except KeyboardInterrupt:
            logger.info("Continuous mode stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in continuous mode: {e}")
            time.sleep(600)  # Wait 10 minutes on error

def run_manual_mode():
    """Run manual/interactive mode"""
    logger = setup_logger("ManualMode")
    logger.info("Starting manual mode")
    
    print("\nManual Mode - Choose your tools:")
    print("1. Reconnaissance")
    print("2. Vulnerability Scanning")
    print("3. Web Application Testing")
    print("4. Target Discovery")
    print("5. Generate Report")
    print("6. Exit")
    
    while True:
        choice = input("\nSelect option (1-6): ")
        
        if choice == "1":
            target = input("Enter target IP/domain: ")
            from modules.reconnaissance import ReconModule
            recon = ReconModule()
            results = recon.comprehensive_scan(target)
            print(f"Reconnaissance results: {results}")
            
        elif choice == "2":
            target = input("Enter target IP/domain: ")
            from modules.scanning import ScanningModule
            scanner = ScanningModule()
            results = scanner.comprehensive_scan(target)
            print(f"Scan results: {results}")
            
        elif choice == "3":
            target = input("Enter target URL: ")
            from modules.web_app_testing import WebAppTester
            tester = WebAppTester()
            results = tester.comprehensive_test(target)
            print(f"Web app test results: {results}")
            
        elif choice == "4":
            targets = discover_targets()
            print(f"Discovered targets: {targets}")
            
        elif choice == "5":
            print("Report generation...")
            reporter = SecurityReporter()
            # Interactive report generation would go here
            
        elif choice == "6":
            logger.info("Exiting manual mode")
            break
        else:
            print("Invalid choice. Please select 1-6.")

def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="AI_HackerOS - Educational Cybersecurity Research Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --target 192.168.1.100 --auto
  python main.py --target auto-discover --auto
  python main.py --continuous
  python main.py --manual
  python main.py --install-tools
        """
    )
    
    parser.add_argument("--target", "-t", help="Target IP address or domain (use 'auto-discover' for autonomous target discovery)")
    parser.add_argument("--auto", "-a", action="store_true", help="Run in autonomous mode")
    parser.add_argument("--continuous", "-c", action="store_true", help="Run in continuous autonomous mode")
    parser.add_argument("--manual", "-m", action="store_true", help="Run in manual mode")
    parser.add_argument("--install-tools", action="store_true", help="Install required tools")
    parser.add_argument("--skip-checks", action="store_true", help="Skip prerequisite checks")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Set up logging level
    log_level = logging.DEBUG if args.verbose else logging.INFO

    # Configure root logger first
    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        stream=sys.stdout)

    # Now, get the logger for the main module
    logger = setup_logger("Main", level=log_level)

    # Ensure directories exist
    config.ensure_directories()

    print_banner()
    
    # Install tools if requested
    if args.install_tools:
        logger.info("Installing all required tools...")
        installer = ToolsInstaller()
        installer.ensure_all_tools_installed()
        logger.info("Tool installation process finished.")
        return
    


    # Launch Burp Suite
    logger.info("Initializing Burp Suite launcher...")
    burp_launcher = BurpLauncher()
    burp_launcher.launch()

    try:
        # Determine mode
        if args.continuous:
            run_continuous_mode()
        elif args.auto and args.target:
            run_autonomous_mode(args.target)
        elif args.auto and not args.target:
            run_autonomous_mode("auto-discover")
        elif args.manual:
            run_manual_mode()
        elif args.target:
            print(f"Target specified: {args.target}")
            print("Use --auto for autonomous mode or --manual for manual mode")
        else:
            print("No mode specified. Use --help for usage information")
            print("\nQuick start:")
            print("  Autonomous mode: python main.py --target <target> --auto")
            print("  Auto-discovery:  python main.py --auto")
            print("  Continuous mode: python main.py --continuous")
            print("  Manual mode:     python main.py --manual")
    finally:
        # Ensure Burp Suite is shut down
        logger.info("Shutting down Burp Suite...")
        burp_launcher.shutdown()

if __name__ == "__main__":
    main()
