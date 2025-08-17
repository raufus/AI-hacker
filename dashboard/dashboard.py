"""
Modern web-based dashboard for security monitoring
"""
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Dict, List, Any
import json
import os
from datetime import datetime
from pathlib import Path

app = FastAPI(
    title="AI_HackerOS Dashboard",
    description="Web-based dashboard for security monitoring",
    version="1.0.0"
)

# Mount static files
dashboard_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=dashboard_dir / "static"), name="static")
templates = Jinja2Templates(directory=dashboard_dir / "templates")

class DashboardData:
    def __init__(self):
        self._load_data()
        self._setup_metrics()
    
    def _load_data(self):
        """Load dashboard data"""
        self.data = {
            "vulnerabilities": self._load_vulnerabilities(),
            "assets": self._load_assets(),
            "scans": self._load_scans(),
            "metrics": self._calculate_metrics()
        }
    
    def _load_vulnerabilities(self) -> List[Dict]:
        """Load vulnerability data"""
        try:
            with open("data/vulnerabilities.json", 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _load_assets(self) -> List[Dict]:
        """Load asset data"""
        try:
            with open("data/assets.json", 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _load_scans(self) -> List[Dict]:
        """Load scan history"""
        try:
            with open("data/scans.json", 'r') as f:
                return json.load(f)
        except:
            return []
    
    def _calculate_metrics(self) -> Dict:
        """Calculate dashboard metrics"""
        return {
            "total_vulnerabilities": len(self.data["vulnerabilities"]),
            "critical_vulns": len([
                v for v in self.data["vulnerabilities"] 
                if v.get("severity") == "critical"
            ]),
            "recent_scans": len([
                s for s in self.data["scans"] 
                if (datetime.now() - datetime.fromisoformat(s.get("timestamp", ""))).days < 7
            ])
        }
    
    def _setup_metrics(self):
        """Setup real-time metrics"""
        self.metrics = {
            "cpu_usage": 0,
            "memory_usage": 0,
            "network_traffic": 0,
            "active_scans": 0
        }
        
        # Update metrics every second
        import threading
        def update_metrics():
            while True:
                self._update_metrics()
                time.sleep(1)
        
        threading.Thread(target=update_metrics, daemon=True).start()
    
    def _update_metrics(self):
        """Update real-time metrics"""
        try:
            import psutil
            self.metrics["cpu_usage"] = psutil.cpu_percent()
            self.metrics["memory_usage"] = psutil.virtual_memory().percent
            # Add more metrics as needed
        except:
            pass

dashboard_data = DashboardData()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "data": dashboard_data.data,
            "metrics": dashboard_data.metrics
        }
    )

@app.get("/api/vulnerabilities")
async def get_vulnerabilities():
    """Get vulnerability data"""
    return dashboard_data.data["vulnerabilities"]

@app.get("/api/assets")
async def get_assets():
    """Get asset data"""
    return dashboard_data.data["assets"]

@app.get("/api/scans")
async def get_scans():
    """Get scan history"""
    return dashboard_data.data["scans"]

@app.get("/api/metrics")
async def get_metrics():
    """Get real-time metrics"""
    return dashboard_data.metrics
