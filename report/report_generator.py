"""
Advanced security report generation system
"""
import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from typing import Dict, List

class SecurityReportGenerator:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_markdown_report(self, data: Dict) -> str:
        """Generate detailed markdown report"""
        template = self.env.get_template('report_template.md.j2')
        report_path = os.path.join(self.reports_dir, f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        
        with open(report_path, 'w') as f:
            f.write(template.render(
                timestamp=datetime.now().isoformat(),
                **data
            ))
        
        return report_path
    
    def generate_html_report(self, data: Dict) -> str:
        """Generate interactive HTML report"""
        template = self.env.get_template('report_template.html.j2')
        report_path = os.path.join(self.reports_dir, f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        
        with open(report_path, 'w') as f:
            f.write(template.render(
                timestamp=datetime.now().isoformat(),
                **data
            ))
        
        return report_path
    
    def generate_json_report(self, data: Dict) -> str:
        """Generate structured JSON report"""
        report_path = os.path.join(self.reports_dir, f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(report_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                **data
            }, f, indent=4)
        
        return report_path
    
    def generate_executive_summary(self, data: Dict) -> str:
        """Generate executive summary"""
        template = self.env.get_template('executive_summary.j2')
        report_path = os.path.join(self.reports_dir, f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        
        with open(report_path, 'w') as f:
            f.write(template.render(
                timestamp=datetime.now().isoformat(),
                **data
            ))
        
        return report_path
    
    def generate_vulnerability_matrix(self, vulnerabilities: List[Dict]) -> Dict:
        """Generate vulnerability matrix"""
        matrix = {
            "high": [],
            "medium": [],
            "low": [],
            "info": []
        }
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "info")
            matrix[severity].append({
                "name": vuln.get("name"),
                "description": vuln.get("description"),
                "cve": vuln.get("cve"),
                "fix": vuln.get("fix")
            })
        
        return matrix
    
    def generate_risk_assessment(self, findings: List[Dict]) -> Dict:
        """Generate risk assessment report"""
        assessment = {
            "total_findings": len(findings),
            "critical_findings": 0,
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
            "recommendations": []
        }
        
        for finding in findings:
            severity = finding.get("severity", "low")
            if severity == "critical":
                assessment["critical_findings"] += 1
            elif severity == "high":
                assessment["high_risk"] += 1
            elif severity == "medium":
                assessment["medium_risk"] += 1
            else:
                assessment["low_risk"] += 1
                
            assessment["recommendations"].append({
                "finding": finding.get("name"),
                "recommendation": finding.get("fix", "N/A"),
                "priority": severity
            })
        
        return assessment
    
    def generate_compliance_report(self, findings: List[Dict], standard: str = "OWASP") -> Dict:
        """Generate compliance report"""
        compliance = {
            "standard": standard,
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "non_compliant": []
        }
        
        for finding in findings:
            if finding.get("standard", "") == standard:
                compliance["total_checks"] += 1
                if finding.get("status", "failed") == "failed":
                    compliance["failed"] += 1
                    compliance["non_compliant"].append({
                        "requirement": finding.get("requirement"),
                        "details": finding.get("description"),
                        "evidence": finding.get("evidence")
                    })
                else:
                    compliance["passed"] += 1
        
        return compliance
