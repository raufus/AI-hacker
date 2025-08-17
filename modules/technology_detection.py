
"""
Web technology detection and fingerprinting
"""
import requests
import logging
import subprocess
import json
from typing import Dict, List, Any
import re

class TechnologyDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
    
    def run_whatweb(self, target: str) -> Dict[str, Any]:
        """Run WhatWeb for technology detection"""
        try:
            result = subprocess.run([
                "whatweb", "--log-json=/tmp/whatweb.json", target
            ], capture_output=True, text=True, timeout=60)
            
            technologies = []
            try:
                with open("/tmp/whatweb.json", "r") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            for plugin in data.get("plugins", {}):
                                technologies.append({
                                    "name": plugin,
                                    "version": data["plugins"][plugin].get("version", ["Unknown"])[0],
                                    "confidence": "High",
                                    "source": "WhatWeb"
                                })
            except Exception as e:
                self.logger.error(f"Failed to parse WhatWeb output: {e}")
            
            return {"technologies": technologies}
            
        except Exception as e:
            self.logger.error(f"WhatWeb failed: {e}")
            return {"technologies": []}
    
    def detect_from_headers(self, target: str) -> List[Dict[str, Any]]:
        """Detect technologies from HTTP headers"""
        technologies = []
        
        try:
            response = self.session.get(target, timeout=10)
            headers = response.headers
            
            # Common header-based detections
            detections = {
                'Server': 'Web Server',
                'X-Powered-By': 'Backend Technology',
                'X-Generator': 'CMS/Framework',
                'X-Drupal-Cache': 'Drupal CMS',
                'X-Pingback': 'WordPress',
                'Set-Cookie': 'Session Management'
            }
            
            for header, tech_type in detections.items():
                if header in headers:
                    technologies.append({
                        "name": headers[header],
                        "type": tech_type,
                        "confidence": "High",
                        "source": f"HTTP Header: {header}"
                    })
            
            # Check for specific patterns
            if 'PHPSESSID' in response.text:
                technologies.append({
                    "name": "PHP",
                    "type": "Programming Language",
                    "confidence": "High",
                    "source": "Session Cookie"
                })
            
            if 'wp-content' in response.text or 'wp-includes' in response.text:
                technologies.append({
                    "name": "WordPress",
                    "type": "CMS",
                    "confidence": "High",
                    "source": "URL Pattern"
                })
                
        except Exception as e:
            self.logger.error(f"Header detection failed: {e}")
        
        return technologies
    
    def detect_from_content(self, target: str) -> List[Dict[str, Any]]:
        """Detect technologies from page content"""
        technologies = []
        
        try:
            response = self.session.get(target, timeout=10)
            content = response.text.lower()
            
            # Technology signatures
            signatures = {
                'wordpress': {'name': 'WordPress', 'type': 'CMS'},
                'drupal': {'name': 'Drupal', 'type': 'CMS'},
                'joomla': {'name': 'Joomla', 'type': 'CMS'},
                'jquery': {'name': 'jQuery', 'type': 'JavaScript Library'},
                'bootstrap': {'name': 'Bootstrap', 'type': 'CSS Framework'},
                'angular': {'name': 'AngularJS', 'type': 'JavaScript Framework'},
                'react': {'name': 'React', 'type': 'JavaScript Framework'},
                'vue.js': {'name': 'Vue.js', 'type': 'JavaScript Framework'},
                'apache': {'name': 'Apache', 'type': 'Web Server'},
                'nginx': {'name': 'Nginx', 'type': 'Web Server'},
                'php': {'name': 'PHP', 'type': 'Programming Language'},
                'asp.net': {'name': 'ASP.NET', 'type': 'Web Framework'},
                'laravel': {'name': 'Laravel', 'type': 'PHP Framework'},
                'django': {'name': 'Django', 'type': 'Python Framework'},
                'rails': {'name': 'Ruby on Rails', 'type': 'Ruby Framework'}
            }
            
            for signature, info in signatures.items():
                if signature in content:
                    technologies.append({
                        "name": info['name'],
                        "type": info['type'],
                        "confidence": "Medium",
                        "source": "Content Analysis"
                    })
            
            # Check meta tags
            meta_patterns = [
                r'<meta name="generator" content="([^"]+)"',
                r'<meta name="author" content="([^"]+)"',
                r'<meta name="description" content="([^"]+)"'
            ]
            
            for pattern in meta_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    technologies.append({
                        "name": match,
                        "type": "Meta Information",
                        "confidence": "Low",
                        "source": "Meta Tag"
                    })
                    
        except Exception as e:
            self.logger.error(f"Content detection failed: {e}")
        
        return technologies
    
    def comprehensive_detection(self, target: str) -> Dict[str, Any]:
        """Run comprehensive technology detection"""
        self.logger.info(f"Starting technology detection for {target}")
        
        all_technologies = []
        
        # Run different detection methods
        methods = [
            ("WhatWeb", lambda: self.run_whatweb(target).get("technologies", [])),
            ("Headers", lambda: self.detect_from_headers(target)),
            ("Content", lambda: self.detect_from_content(target))
        ]
        
        for method_name, method_func in methods:
            try:
                technologies = method_func()
                all_technologies.extend(technologies)
            except Exception as e:
                self.logger.error(f"Technology detection method {method_name} failed: {e}")
        
        # Deduplicate and organize results
        unique_technologies = self.deduplicate_technologies(all_technologies)
        
        result = {
            "target": target,
            "technologies": unique_technologies,
            "summary": self.create_tech_summary(unique_technologies)
        }
        
        self.logger.info(f"Detected {len(unique_technologies)} technologies for {target}")
        return result
    
    def deduplicate_technologies(self, technologies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate technology detections"""
        seen = {}
        unique_techs = []
        
        for tech in technologies:
            name = tech.get("name", "").lower()
            
            if name not in seen:
                seen[name] = tech
                unique_techs.append(tech)
            else:
                # Keep the one with higher confidence
                existing = seen[name]
                confidence_order = {"High": 3, "Medium": 2, "Low": 1}
                
                if confidence_order.get(tech.get("confidence", "Low"), 1) > \
                   confidence_order.get(existing.get("confidence", "Low"), 1):
                    seen[name] = tech
                    # Replace in list
                    for i, t in enumerate(unique_techs):
                        if t.get("name", "").lower() == name:
                            unique_techs[i] = tech
                            break
        
        return unique_techs
    
    def create_tech_summary(self, technologies: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Create a summary of detected technologies by category"""
        summary = {}
        
        for tech in technologies:
            tech_type = tech.get("type", "Unknown")
            tech_name = tech.get("name", "Unknown")
            
            if tech_type not in summary:
                summary[tech_type] = []
            
            if tech_name not in summary[tech_type]:
                summary[tech_type].append(tech_name)
        
        return summary
