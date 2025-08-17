"""
Example usage of AI_HackerOS
"""
from modules.scanning import NetworkScanner, WebScanner
from modules.exploitation import ExploitationModule
from report.advanced_reporter import AdvancedSecurityReporter
from ai.analysis_engine import SecurityAIEngine
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_basic_scan(target: str):
    """Run a basic scan with all components"""
    # Initialize modules
    network_scanner = NetworkScanner()
    web_scanner = WebScanner()
    exploitation = ExploitationModule()
    reporter = AdvancedSecurityReporter()
    ai_engine = SecurityAIEngine()
    
    try:
        # 1. Network Scan
        logger.info("Starting network scan...")
        network_results = network_scanner.scan(target)
        logger.info(f"Network scan completed. Found {len(network_results)} hosts")
        
        # 2. Web Scan
        logger.info("Starting web scan...")
        web_results = web_scanner.scan(target)
        logger.info(f"Web scan completed. Found {len(web_results)} web applications")
        
        # 3. AI Analysis
        logger.info("Starting AI analysis...")
        ai_analysis = ai_engine.analyze_vulnerability(web_results)
        logger.info(f"AI analysis completed. Severity: {ai_analysis['severity']}")
        
        # 4. Exploitation
        if ai_analysis['severity'] in ['high', 'critical']:
            logger.info("Starting exploitation...")
            exploitation_results = exploitation.exploit_target(target)
            logger.info(f"Exploitation completed. Found {len(exploitation_results)} vulnerabilities")
        
        # 5. Generate Report
        logger.info("Generating comprehensive report...")
        report_path = reporter.generate_comprehensive_report({
            'target': target,
            'network_results': network_results,
            'web_results': web_results,
            'ai_analysis': ai_analysis,
            'exploitation_results': exploitation_results if 'exploitation_results' in locals() else []
        })
        logger.info(f"Report generated successfully at: {report_path}")
        
    except Exception as e:
        logger.error(f"Error during scan: {str(e)}")
        raise

def main():
    # Example target (replace with your target)
    target = "192.168.1.1"
    
    # Run the scan
    run_basic_scan(target)

if __name__ == "__main__":
    main()
