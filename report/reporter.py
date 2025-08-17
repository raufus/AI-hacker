
"""
Markdown/HTML/PDF report generation
"""
import json
import datetime
from typing import Dict, List, Any
import os

class SecurityReporter:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.report_data = {
            "metadata": {
                "generated": datetime.datetime.now().isoformat(),
                "target": None,
                "duration": None
            },
            "executive_summary": "",
            "reconnaissance": {},
            "vulnerabilities": [],
            "exploitation_results": [],
            "recommendations": []
        }
    
    def set_target(self, target: str):
        """Set the target for the report"""
        self.report_data["metadata"]["target"] = target
    
    def add_reconnaissance_data(self, data: Dict[str, Any]):
        """Add reconnaissance findings"""
        self.report_data["reconnaissance"].update(data)
    
    def add_vulnerability(self, vuln: Dict[str, Any]):
        """Add vulnerability finding"""
        self.report_data["vulnerabilities"].append(vuln)
    
    def add_exploitation_result(self, result: Dict[str, Any]):
        """Add exploitation result"""
        self.report_data["exploitation_results"].append(result)
    
    def generate_markdown_report(self, filename: str = None) -> str:
        """Generate Markdown report"""
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"security_report_{timestamp}.md"
        
        target = self.report_data["metadata"]["target"]
        generated = self.report_data["metadata"]["generated"]
        
        markdown_content = f"""# Security Assessment Report
        
## Executive Summary
Target: {target}
Generated: {generated}

## Reconnaissance Results
### Network Information
- Target: {target}
- Open Ports: {len(self.report_data["reconnaissance"].get("nmap", {}).get("ports", []))}
- Services Detected: {len(self.report_data["reconnaissance"].get("nmap", {}).get("services", []))}

### Web Technologies
{json.dumps(self.report_data["reconnaissance"].get("web_tech", {}), indent=2)}

## Vulnerabilities Found
Total Vulnerabilities: {len(self.report_data["vulnerabilities"])}

"""
        
        for i, vuln in enumerate(self.report_data["vulnerabilities"], 1):
            markdown_content += f"""### Vulnerability {i}: {vuln.get("type", "Unknown")}
- **Severity**: {vuln.get("severity", "Medium")}
- **Description**: {vuln.get("description", "No description available")}
- **Impact**: {vuln.get("impact", "Not assessed")}

"""
        
        markdown_content += """## Recommendations
1. Apply security patches for identified vulnerabilities
2. Implement proper input validation
3. Use HTTPS for all web communications
4. Regular security assessments

## Disclaimer
This report is for educational and authorized testing purposes only.
"""
        
        full_path = os.path.join(self.output_dir, filename)
        with open(full_path, 'w') as f:
            f.write(markdown_content)
        
        return full_path
    
    def generate_html_report(self, filename: str = None) -> str:
        """Generate HTML report"""
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"security_report_{timestamp}.html"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Security Assessment Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; }}
        .vulnerability {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; }}
        .critical {{ border-color: #ff0000; }}
        .high {{ border-color: #ff6600; }}
        .medium {{ border-color: #ffcc00; }}
        .low {{ border-color: #00cc00; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Security Assessment Report</h1>
        <p><strong>Target:</strong> {self.report_data["metadata"]["target"]}</p>
        <p><strong>Generated:</strong> {self.report_data["metadata"]["generated"]}</p>
    </div>
    
    <h2>Executive Summary</h2>
    <p>Total vulnerabilities found: {len(self.report_data["vulnerabilities"])}</p>
    
    <h2>Vulnerabilities</h2>
"""
        
        for vuln in self.report_data["vulnerabilities"]:
            severity = vuln.get("severity", "medium").lower()
            html_content += f"""
    <div class="vulnerability {severity}">
        <h3>{vuln.get("type", "Unknown Vulnerability")}</h3>
        <p><strong>Severity:</strong> {vuln.get("severity", "Medium")}</p>
        <p><strong>Description:</strong> {vuln.get("description", "No description available")}</p>
    </div>
"""
        
        html_content += """
    <h2>Disclaimer</h2>
    <p>This report is for educational and authorized testing purposes only.</p>
</body>
</html>
"""
        
        full_path = os.path.join(self.output_dir, filename)
        with open(full_path, 'w') as f:
            f.write(html_content)
        
        return full_path
    
    def generate_json_report(self, filename: str = None) -> str:
        """Generate JSON report"""
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"security_report_{timestamp}.json"
        
        full_path = os.path.join(self.output_dir, filename)
        with open(full_path, 'w') as f:
            json.dump(self.report_data, f, indent=2)
        
        return full_path
