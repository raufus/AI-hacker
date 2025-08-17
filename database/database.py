"""
Database management system for storing scan results and findings
"""
import sqlite3
import json
from datetime import datetime
import os
from typing import Dict, List, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "data/ai_hackeros.db"):
        self.db_path = db_path
        self._setup_database()
    
    def _setup_database(self):
        """Create database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create targets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT NOT NULL,
                    type TEXT,
                    status TEXT,
                    last_scanned TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create scan_results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id INTEGER,
                    scan_type TEXT,
                    results TEXT,
                    status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (target_id) REFERENCES targets (id)
                )
            ''')
            
            # Create vulnerabilities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vulnerabilities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    vulnerability TEXT,
                    severity TEXT,
                    details TEXT,
                    status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scan_id) REFERENCES scan_results (id)
                )
            ''')
            
            # Create findings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    finding_type TEXT,
                    details TEXT,
                    status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (scan_id) REFERENCES scan_results (id)
                )
            ''')
            
            conn.commit()
    
    def add_target(self, target: str, target_type: str = "unknown") -> int:
        """Add new target to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO targets (target, type, status, last_scanned)
                VALUES (?, ?, ?, ?)
            ''', (target, target_type, "pending", datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid
    
    def add_scan_result(self, target_id: int, scan_type: str, results: Dict) -> int:
        """Add scan results to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scan_results (target_id, scan_type, results, status)
                VALUES (?, ?, ?, ?)
            ''', (target_id, scan_type, json.dumps(results), "completed"))
            conn.commit()
            return cursor.lastrowid
    
    def add_vulnerability(self, scan_id: int, vulnerability: Dict) -> int:
        """Add vulnerability finding"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO vulnerabilities (scan_id, vulnerability, severity, details, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                scan_id,
                vulnerability.get("name", "unknown"),
                vulnerability.get("severity", "unknown"),
                json.dumps(vulnerability),
                "new"
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_scan_history(self, target: str) -> List[Dict]:
        """Get scan history for a target"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.*, t.target
                FROM scan_results s
                JOIN targets t ON s.target_id = t.id
                WHERE t.target = ?
                ORDER BY s.created_at DESC
            ''', (target,))
            
            return [{
                "id": row[0],
                "target": row[6],
                "scan_type": row[2],
                "status": row[4],
                "created_at": row[5]
            } for row in cursor.fetchall()]
    
    def get_vulnerabilities(self, target: str) -> List[Dict]:
        """Get all vulnerabilities for a target"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT v.*, s.scan_type, t.target
                FROM vulnerabilities v
                JOIN scan_results s ON v.scan_id = s.id
                JOIN targets t ON s.target_id = t.id
                WHERE t.target = ?
                ORDER BY v.severity DESC
            ''', (target,))
            
            return [{
                "id": row[0],
                "scan_type": row[7],
                "target": row[8],
                "vulnerability": row[2],
                "severity": row[3],
                "details": json.loads(row[4]),
                "status": row[5],
                "created_at": row[6]
            } for row in cursor.fetchall()]
    
    def update_vulnerability_status(self, vuln_id: int, status: str):
        """Update vulnerability status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE vulnerabilities
                SET status = ?
                WHERE id = ?
            ''', (status, vuln_id))
            conn.commit()
    
    def get_target_stats(self, target: str) -> Dict:
        """Get statistics for a target"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get total scans
            cursor.execute('''
                SELECT COUNT(*)
                FROM scan_results s
                JOIN targets t ON s.target_id = t.id
                WHERE t.target = ?
            ''', (target,))
            total_scans = cursor.fetchone()[0]
            
            # Get vulnerability count by severity
            cursor.execute('''
                SELECT severity, COUNT(*)
                FROM vulnerabilities v
                JOIN scan_results s ON v.scan_id = s.id
                JOIN targets t ON s.target_id = t.id
                WHERE t.target = ?
                GROUP BY severity
            ''', (target,))
            severity_counts = dict(cursor.fetchall())
            
            return {
                "total_scans": total_scans,
                "vulnerabilities": {
                    "critical": severity_counts.get("critical", 0),
                    "high": severity_counts.get("high", 0),
                    "medium": severity_counts.get("medium", 0),
                    "low": severity_counts.get("low", 0)
                }
            }
    
    def export_data(self, target: str, format: str = "json") -> str:
        """Export data for a target"""
        data = {
            "target": target,
            "stats": self.get_target_stats(target),
            "vulnerabilities": self.get_vulnerabilities(target),
            "scan_history": self.get_scan_history(target)
        }
        
        if format == "json":
            return json.dumps(data, indent=4)
        # Add more formats as needed
        return json.dumps(data, indent=4)
