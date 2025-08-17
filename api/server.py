"""
REST API server for AI_HackerOS
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime
from security.auth import AuthManager
from database.database import DatabaseManager
from modules.scanning import NetworkScanner, WebScanner

app = FastAPI(
    title="AI_HackerOS API",
    description="REST API for AI_HackerOS penetration testing platform",
    version="1.0.0"
)

# Initialize components
auth_manager = AuthManager()
api_key_header = APIKeyHeader(name="X-API-Key")
db_manager = DatabaseManager()
network_scanner = NetworkScanner()
web_scanner = WebScanner()

class ScanRequest(BaseModel):
    target: str
    scan_type: str
    options: Optional[dict] = None

class AuthRequest(BaseModel):
    username: str
    password: str

def verify_api_key(api_key: str = Depends(api_key_header)):
    """Verify API key middleware"""
    user_info = auth_manager.verify_api_key(api_key)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return user_info

@app.post("/auth/login", response_model=dict)
async def login(request: AuthRequest):
    """Authenticate user and return API key"""
    if not auth_manager.authenticate_user(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return {
        "api_key": auth_manager.auth_data["users"][request.username]["api_key"],
        "permissions": auth_manager.get_user_permissions(request.username)
    }

@app.post("/scan", response_model=dict)
async def start_scan(request: ScanRequest, user_info: dict = Depends(verify_api_key)):
    """Start a new scan"""
    # Check permissions
    if "scan" not in user_info["permissions"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    # Get scanner based on scan type
    scanner = None
    if request.scan_type == "network":
        scanner = network_scanner
    elif request.scan_type == "web":
        scanner = web_scanner
    
    if not scanner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid scan type"
        )
    
    # Start scan
    try:
        target_id = db_manager.add_target(request.target)
        results = scanner.scan(request.target, **(request.options or {}))
        scan_id = db_manager.add_scan_result(target_id, request.scan_type, results)
        
        return {
            "scan_id": scan_id,
            "status": "completed",
            "target": request.target,
            "scan_type": request.scan_type
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/scans/{target}", response_model=dict)
async def get_scan_history(target: str, user_info: dict = Depends(verify_api_key)):
    """Get scan history for a target"""
    if "view" not in user_info["permissions"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    return db_manager.get_scan_history(target)

@app.get("/vulnerabilities/{target}", response_model=dict)
async def get_vulnerabilities(target: str, user_info: dict = Depends(verify_api_key)):
    """Get vulnerabilities for a target"""
    if "view" not in user_info["permissions"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    return db_manager.get_vulnerabilities(target)

@app.get("/stats/{target}", response_model=dict)
async def get_target_stats(target: str, user_info: dict = Depends(verify_api_key)):
    """Get statistics for a target"""
    if "view" not in user_info["permissions"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    return db_manager.get_target_stats(target)

@app.post("/vulnerability/{vuln_id}/status", response_model=dict)
async def update_vulnerability_status(
    vuln_id: int,
    status: str,
    user_info: dict = Depends(verify_api_key)
):
    """Update vulnerability status"""
    if "manage" not in user_info["permissions"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    db_manager.update_vulnerability_status(vuln_id, status)
    return {"status": "updated"}

@app.get("/export/{target}")
async def export_data(
    target: str,
    format: str = "json",
    user_info: dict = Depends(verify_api_key)
):
    """Export data for a target"""
    if "export" not in user_info["permissions"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    return db_manager.export_data(target, format)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
