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
            
            # Create engagements table (Security Control requirement)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS engagements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'planned',
                    start_date TEXT,
                    end_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create targets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    engagement_id INTEGER,
                    target TEXT NOT NULL,
                    type TEXT,
                    status TEXT,
                    authorized BOOLEAN DEFAULT FALSE,
                    last_scanned TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (engagement_id) REFERENCES engagements (id)
                )
            ''')

            # Create jobs table (Task state machine support)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    engagement_id INTEGER,
                    target_id INTEGER,
                    module TEXT NOT NULL,
                    status TEXT DEFAULT 'queued',
                    input_data TEXT,
                    output_data TEXT,
                    error_message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (engagement_id) REFERENCES engagements (id),
                    FOREIGN KEY (target_id) REFERENCES targets (id)
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
    
    def create_engagement(self, name: str, description: str = "") -> int:
        """Create a new authorized engagement"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO engagements (name, description, status)
                VALUES (?, ?, ?)
            ''', (name, description, "active"))
            conn.commit()
            return cursor.lastrowid

    def add_target(self, engagement_id: int, target: str, target_type: str = "unknown", authorized: bool = False) -> int:
        """Add new target to database, must be linked to an engagement"""
        # Server-side validation
        if not target or not isinstance(target, str) or len(target) < 3:
            raise ValueError("Invalid target format")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Verify engagement exists
            cursor.execute("SELECT id FROM engagements WHERE id = ?", (engagement_id,))
            if not cursor.fetchone():
                raise ValueError("Engagement does not exist")

            cursor.execute('''
                INSERT INTO targets (engagement_id, target, type, status, authorized, last_scanned)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (engagement_id, target, target_type, "pending", authorized, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid

    def is_target_authorized(self, target: str) -> bool:
        """Check if a target is explicitly authorized"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT authorized FROM targets WHERE target = ? AND authorized = 1
            ''', (target,))
            return cursor.fetchone() is not None

    def create_job(self, engagement_id: int, target_id: int, module: str, input_data: Dict = None) -> int:
        """Create a new execution job"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Strict verification: Ensure target belongs to the engagement and is authorized
            cursor.execute('''
                SELECT t.authorized, e.status
                FROM targets t
                JOIN engagements e ON t.engagement_id = e.id
                WHERE t.id = ? AND t.engagement_id = ?
            ''', (target_id, engagement_id))

            row = cursor.fetchone()
            if not row:
                raise ValueError("Target does not belong to this engagement or does not exist")

            authorized, eng_status = row
            if not authorized:
                raise ValueError("Cannot create job for unauthorized target")
            if eng_status != 'active':
                raise ValueError("Cannot create job for inactive engagement")

            cursor.execute('''
                INSERT INTO jobs (engagement_id, target_id, module, status, input_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (engagement_id, target_id, module, 'queued', json.dumps(input_data) if input_data else "{}"))
            conn.commit()
            return cursor.lastrowid

    def claim_job(self) -> Optional[tuple]:
        """Claim a queued job for a worker with transaction safety and authorization checks"""
        with sqlite3.connect(self.db_path, isolation_level=None) as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            try:
                cursor.execute('''
                    SELECT j.id, j.module, t.target, j.input_data
                    FROM jobs j
                    JOIN targets t ON j.target_id = t.id
                    JOIN engagements e ON j.engagement_id = e.id
                    WHERE j.status = 'queued'
                      AND t.authorized = 1
                      AND e.status = 'active'
                    ORDER BY j.created_at ASC LIMIT 1
                ''')
                job = cursor.fetchone()

                if job:
                    job_id = job[0]
                    cursor.execute("UPDATE jobs SET status = 'running', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (job_id,))
                    conn.commit()
                    return (job[0], job[1], job[2], json.loads(job[3] or "{}"))
                conn.commit()
                return None
            except Exception as e:
                conn.rollback()
                raise e

    def update_job_status(self, job_id: int, status: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE jobs SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (status, job_id))
            conn.commit()

    def update_job_result(self, job_id: int, status: str, result_data: Dict):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Save error message if failed, else output_data
            if status == 'failed':
                cursor.execute("UPDATE jobs SET status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                               (status, json.dumps(result_data), job_id))
            else:
                cursor.execute("UPDATE jobs SET status = ?, output_data = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                               (status, json.dumps(result_data), job_id))

                # If completed successfully, add a scan result
                cursor.execute("SELECT target_id, module FROM jobs WHERE id = ?", (job_id,))
                job_info = cursor.fetchone()
                if job_info:
                    target_id, module = job_info
                    cursor.execute('''
                        INSERT INTO scan_results (target_id, scan_type, results, status)
                        VALUES (?, ?, ?, ?)
                    ''', (target_id, module, json.dumps(result_data), "completed"))
                    scan_id = cursor.lastrowid

            conn.commit()

            if status != 'failed' and job_info:
                # Create findings if result_data has a 'vulnerabilities' key
                if 'vulnerabilities' in result_data and isinstance(result_data['vulnerabilities'], list):
                    for vuln in result_data['vulnerabilities']:
                        self.add_vulnerability(scan_id, vuln)
    
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
