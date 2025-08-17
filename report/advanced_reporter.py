"""
Advanced reporting system with detailed analysis and visualization
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, List, Any
import os
from datetime import datetime

class AdvancedSecurityReporter:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_comprehensive_report(self, scan_results: Dict) -> str:
        """Generate comprehensive security report"""
        report_path = os.path.join(
            self.output_dir,
            f"comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        # Create PDF
        c = canvas.Canvas(report_path, pagesize=letter)
        width, height = letter
        
        # Title page
        self._add_title_page(c, scan_results)
        
        # Executive summary
        self._add_executive_summary(c, scan_results)
        
        # Vulnerability analysis
        self._add_vulnerability_analysis(c, scan_results)
        
        # Risk assessment
        self._add_risk_assessment(c, scan_results)
        
        # Recommendations
        self._add_recommendations(c, scan_results)
        
        # Save PDF
        c.save()
        
        return report_path
    
    def _add_title_page(self, c: canvas.Canvas, scan_results: Dict):
        """Add title page to report"""
        c.setFont("Helvetica-Bold", 24)
        c.drawString(100, 750, "Security Assessment Report")
        
        c.setFont("Helvetica", 12)
        c.drawString(100, 700, f"Target: {scan_results.get('target', 'unknown')}")
        c.drawString(100, 680, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Add logo
        if os.path.exists("assets/logo.png"):
            c.drawImage("assets/logo.png", 400, 700, width=100, height=100)
        
        c.showPage()
    
    def _add_executive_summary(self, c: canvas.Canvas, scan_results: Dict):
        """Add executive summary"""
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Executive Summary")
        
        # Generate summary statistics
        stats = self._generate_summary_stats(scan_results)
        
        # Add summary text
        c.setFont("Helvetica", 12)
        y = 700
        for key, value in stats.items():
            c.drawString(100, y, f"{key}: {value}")
            y -= 20
        
        # Add risk level visualization
        self._add_risk_visualization(c, scan_results)
        
        c.showPage()
    
    def _add_vulnerability_analysis(self, c: canvas.Canvas, scan_results: Dict):
        """Add detailed vulnerability analysis"""
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Vulnerability Analysis")
        
        # Generate vulnerability matrix
        matrix = self._generate_vulnerability_matrix(scan_results)
        
        # Add matrix visualization
        self._add_matrix_visualization(c, matrix)
        
        # Add detailed findings
        y = 650
        for vuln in scan_results.get('vulnerabilities', []):
            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, y, f"Vulnerability: {vuln.get('name', 'Unknown')}")
            
            c.setFont("Helvetica", 10)
            y -= 15
            c.drawString(120, y, f"Severity: {vuln.get('severity', 'Unknown')}")
            y -= 15
            c.drawString(120, y, f"Description: {vuln.get('description', '')}")
            y -= 15
            c.drawString(120, y, f"Recommendation: {vuln.get('fix', '')}")
            y -= 30
            
            if y < 50:
                c.showPage()
                y = 750
        
        c.showPage()
    
    def _add_risk_assessment(self, c: canvas.Canvas, scan_results: Dict):
        """Add risk assessment section"""
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Risk Assessment")
        
        # Generate risk metrics
        metrics = self._calculate_risk_metrics(scan_results)
        
        # Add metrics visualization
        self._add_metrics_visualization(c, metrics)
        
        # Add risk factors
        y = 650
        c.setFont("Helvetica", 12)
        c.drawString(100, y, "Risk Factors:")
        y -= 20
        
        for factor in self._identify_risk_factors(scan_results):
            c.drawString(120, y, f"- {factor}")
            y -= 15
            if y < 50:
                c.showPage()
                y = 750
        
        c.showPage()
    
    def _add_recommendations(self, c: canvas.Canvas, scan_results: Dict):
        """Add detailed recommendations"""
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Recommendations")
        
        # Generate prioritized recommendations
        recommendations = self._generate_prioritized_recommendations(scan_results)
        
        y = 700
        for priority, recs in recommendations.items():
            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, y, f"{priority} Priority:")
            y -= 20
            
            c.setFont("Helvetica", 10)
            for rec in recs:
                c.drawString(120, y, f"- {rec}")
                y -= 15
                if y < 50:
                    c.showPage()
                    y = 750
        
        c.showPage()
    
    def _generate_summary_stats(self, scan_results: Dict) -> Dict:
        """Generate summary statistics"""
        stats = {
            "Total Vulnerabilities": len(scan_results.get('vulnerabilities', [])),
            "Critical Vulnerabilities": len([
                v for v in scan_results.get('vulnerabilities', []) 
                if v.get('severity') == 'critical'
            ]),
            "High Risk": len([
                v for v in scan_results.get('vulnerabilities', []) 
                if v.get('severity') == 'high'
            ]),
            "Exploitable": len([
                v for v in scan_results.get('vulnerabilities', []) 
                if v.get('public_exploit', False)
            ])
        }
        return stats
    
    def _generate_vulnerability_matrix(self, scan_results: Dict) -> pd.DataFrame:
        """Generate vulnerability matrix"""
        matrix = []
        for vuln in scan_results.get('vulnerabilities', []):
            matrix.append({
                "Name": vuln.get('name', 'Unknown'),
                "Severity": vuln.get('severity', 'Unknown'),
                "Category": vuln.get('category', 'Unknown'),
                "Priority": vuln.get('priority', 'Medium'),
                "Status": vuln.get('status', 'Open')
            })
        return pd.DataFrame(matrix)
    
    def _calculate_risk_metrics(self, scan_results: Dict) -> Dict:
        """Calculate risk metrics"""
        metrics = {
            "Vulnerability Density": len(scan_results.get('vulnerabilities', [])) / 
                                  len(scan_results.get('assets', [])),
            "Critical Risk Score": sum(
                1 for v in scan_results.get('vulnerabilities', []) 
                if v.get('severity') == 'critical'
            ) * 10,
            "Exploitability Score": sum(
                v.get('exploitability_score', 0) 
                for v in scan_results.get('vulnerabilities', [])
            )
        }
        return metrics
    
    def _identify_risk_factors(self, scan_results: Dict) -> List[str]:
        """Identify risk factors"""
        factors = []
        
        if len([v for v in scan_results.get('vulnerabilities', []) 
                if v.get('severity') == 'critical']) > 0:
            factors.append("Critical vulnerabilities present")
        
        if len([v for v in scan_results.get('vulnerabilities', []) 
                if v.get('public_exploit', False)]) > 0:
            factors.append("Known exploits available")
        
        if len(scan_results.get('assets', [])) > 100:
            factors.append("Large attack surface")
        
        return factors
