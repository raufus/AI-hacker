"""
Advanced AI-powered analysis engine for security assessment
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, List, Any
import numpy as np
from datetime import datetime
import logging

class SecurityAIEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained AI models"""
        try:
            # Load vulnerability classification model
            self.vuln_classifier = AutoModelForSequenceClassification.from_pretrained(
                "security-models/vulnerability-detector"
            )
            self.vuln_tokenizer = AutoTokenizer.from_pretrained(
                "security-models/vulnerability-detector"
            )
            
            # Load threat assessment model
            self.threat_assessor = AutoModelForSequenceClassification.from_pretrained(
                "security-models/threat-assessor"
            )
            self.threat_tokenizer = AutoTokenizer.from_pretrained(
                "security-models/threat-assessor"
            )
            
            self.logger.info("AI models loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading AI models: {e}")
            raise
    
    def analyze_vulnerability(self, vulnerability: Dict) -> Dict:
        """Analyze vulnerability using AI"""
        try:
            # Prepare input
            input_text = f"""
            Vulnerability Type: {vulnerability.get('type', 'unknown')}
            Description: {vulnerability.get('description', '')}
            Impact: {vulnerability.get('impact', '')}
            Fix: {vulnerability.get('fix', '')}
            """
            
            # Tokenize and classify
            inputs = self.vuln_tokenizer(input_text, return_tensors="pt")
            outputs = self.vuln_classifier(**inputs)
            
            # Get prediction
            prediction = torch.argmax(outputs.logits, dim=1).item()
            confidence = torch.softmax(outputs.logits, dim=1).max().item()
            
            return {
                "severity": self._get_severity(prediction),
                "confidence": confidence,
                "recommendations": self._generate_recommendations(vulnerability),
                "mitigation": self._generate_mitigation(vulnerability)
            }
        except Exception as e:
            self.logger.error(f"Error analyzing vulnerability: {e}")
            return {"error": str(e)}
    
    def assess_threat(self, scan_results: Dict) -> Dict:
        """Assess threat level using AI"""
        try:
            # Prepare input
            input_text = f"""
            Target: {scan_results.get('target', 'unknown')}
            Vulnerabilities: {len(scan_results.get('vulnerabilities', []))}
            Critical: {len([v for v in scan_results.get('vulnerabilities', []) 
                           if v.get('severity') == 'critical'])}
            High: {len([v for v in scan_results.get('vulnerabilities', []) 
                        if v.get('severity') == 'high'])}
            """
            
            # Tokenize and classify
            inputs = self.threat_tokenizer(input_text, return_tensors="pt")
            outputs = self.threat_assessor(**inputs)
            
            # Get prediction
            prediction = torch.argmax(outputs.logits, dim=1).item()
            confidence = torch.softmax(outputs.logits, dim=1).max().item()
            
            return {
                "threat_level": self._get_threat_level(prediction),
                "confidence": confidence,
                "recommendations": self._generate_threat_recommendations(scan_results)
            }
        except Exception as e:
            self.logger.error(f"Error assessing threat: {e}")
            return {"error": str(e)}
    
    def predict_exploitability(self, vulnerability: Dict) -> float:
        """Predict exploitability score"""
        try:
            # Feature extraction
            features = np.array([
                len(vulnerability.get('description', '')),
                len(vulnerability.get('fix', '')),
                vulnerability.get('severity', 'low') in ['high', 'critical'],
                vulnerability.get('cve', '') != '',
                vulnerability.get('public_exploit', False)
            ])
            
            # Predict using pre-trained model
            model = self._load_exploit_model()
            score = model.predict(features.reshape(1, -1))[0]
            
            return float(score)
        except Exception as e:
            self.logger.error(f"Error predicting exploitability: {e}")
            return 0.0
    
    def generate_mitigation_plan(self, scan_results: Dict) -> Dict:
        """Generate comprehensive mitigation plan"""
        try:
            plan = {
                "priority": self._get_mitigation_priority(scan_results),
                "steps": self._generate_mitigation_steps(scan_results),
                "timeline": self._estimate_timeline(scan_results),
                "resources": self._estimate_resources(scan_results)
            }
            
            return plan
        except Exception as e:
            self.logger.error(f"Error generating mitigation plan: {e}")
            return {"error": str(e)}
    
    def _get_severity(self, prediction: int) -> str:
        """Map prediction to severity level"""
        severities = ["info", "low", "medium", "high", "critical"]
        return severities[prediction]
    
    def _get_threat_level(self, prediction: int) -> str:
        """Map prediction to threat level"""
        levels = ["low", "medium", "high", "critical"]
        return levels[prediction]
    
    def _generate_recommendations(self, vulnerability: Dict) -> List[str]:
        """Generate specific recommendations"""
        recommendations = []
        
        if vulnerability.get('severity') in ['high', 'critical']:
            recommendations.append("Implement immediate mitigation")
            recommendations.append("Conduct root cause analysis")
            recommendations.append("Review similar components")
        
        if vulnerability.get('public_exploit', False):
            recommendations.append("Apply emergency patch")
            recommendations.append("Implement temporary controls")
            
        return recommendations
    
    def _generate_mitigation(self, vulnerability: Dict) -> Dict:
        """Generate detailed mitigation steps"""
        return {
            "short_term": self._generate_short_term_mitigation(vulnerability),
            "long_term": self._generate_long_term_mitigation(vulnerability),
            "monitoring": self._generate_monitoring_actions(vulnerability)
        }
