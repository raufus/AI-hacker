import time
import json
import logging
import sqlite3
import traceback
from datetime import datetime
from database.database import DatabaseManager

# Import available modules
from modules.scanning import NetworkScanner, WebScanner, VulnerabilityScanner

class JobWorker:
    def __init__(self, db_path: str = "data/ai_hackeros.db", poll_interval: int = 5):
        self.logger = logging.getLogger("JobWorker")
        self.db_manager = DatabaseManager(db_path=db_path)
        self.poll_interval = poll_interval
        self.running = False

    def start(self):
        """Starts the worker polling loop."""
        self.running = True
        self.logger.info("Worker started, polling for jobs...")
        while self.running:
            try:
                job = self._claim_next_job()
                if job:
                    self._execute_job(job)
                else:
                    time.sleep(self.poll_interval)
            except Exception as e:
                self.logger.error(f"Worker encountered an error: {e}")
                time.sleep(self.poll_interval)

    def stop(self):
        """Stops the worker polling loop."""
        self.running = False
        self.logger.info("Worker stopping...")

    def _claim_next_job(self) -> dict:
        """Atomically claims the next pending job to prevent concurrent execution."""
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            # Find next pending job
            cursor.execute('''
                SELECT id, target_id, module, input_data, engagement_id
                FROM jobs
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT 1
            ''')
            row = cursor.fetchone()

            if not row:
                return None

            job_id, target_id, module, input_data, engagement_id = row

            # Claim it
            cursor.execute('''
                UPDATE jobs SET status = 'running', updated_at = ? WHERE id = ? AND status = 'pending'
            ''', (datetime.now().isoformat(), job_id))

            if cursor.rowcount > 0:
                conn.commit()
                return {
                    'id': job_id,
                    'target_id': target_id,
                    'module': module,
                    'input_data': json.loads(input_data) if input_data else {},
                    'engagement_id': engagement_id
                }
            return None

    def _execute_job(self, job: dict):
        """Executes the given job safely."""
        job_id = job['id']
        target_id = job['target_id']
        module_name = job['module']
        self.logger.info(f"Executing job {job_id} for module '{module_name}'")

        try:
            # 1. Fetch Target details and enforce authorization
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT target, authorized, engagement_id FROM targets WHERE id = ?', (target_id,))
                target_row = cursor.fetchone()

                if not target_row:
                    raise ValueError(f"Target ID {target_id} not found.")

                target_str, authorized, target_eng_id = target_row

                if not authorized:
                    raise PermissionError(f"Target '{target_str}' is not authorized for scanning.")

                if target_eng_id != job['engagement_id']:
                    raise PermissionError(f"Target '{target_str}' does not belong to the job's engagement.")

            # 2. Map module string to actual class
            scanner = self._get_scanner(module_name)
            if not scanner:
                 raise NotImplementedError(f"Module '{module_name}' is not supported.")

            # 3. Execute
            self.logger.info(f"Running {module_name} on target {target_str}")
            # Ensure safe kwargs based on what the scanner supports
            options = job.get('input_data', {})
            results = scanner.scan(target_str, options=options) if module_name == 'VulnerabilityScanner' else scanner.scan(target_str)

            # Record findings if successful and valid format
            if isinstance(results, dict) and "error" not in results:
                if "vulnerabilities" in results:
                     for v in results["vulnerabilities"]:
                         self.db_manager.add_vulnerability(
                            self.db_manager.add_scan_result(target_id, module_name, results),
                            v
                         )

            # 4. Mark job completed
            self._update_job_status(job_id, 'completed', output_data=results)

        except PermissionError as pe:
            self.logger.warning(f"Job {job_id} aborted: {pe}")
            self._update_job_status(job_id, 'failed', error_message=str(pe))
        except Exception as e:
            err_msg = traceback.format_exc()
            self.logger.error(f"Job {job_id} failed: {e}\n{err_msg}")
            self._update_job_status(job_id, 'failed', error_message=str(e))

    def _get_scanner(self, module_name: str):
        if module_name == 'Network Scanner':
            return NetworkScanner()
        elif module_name == 'Web Scanner':
            return WebScanner()
        elif module_name == 'Vulnerability Scanner':
            return VulnerabilityScanner()
        return None

    def _update_job_status(self, job_id: int, status: str, output_data: dict = None, error_message: str = None):
        """Updates the job status and records output or errors."""
        with sqlite3.connect(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            output_str = json.dumps(output_data) if output_data else None
            cursor.execute('''
                UPDATE jobs
                SET status = ?, output_data = ?, error_message = ?, updated_at = ?
                WHERE id = ?
            ''', (status, output_str, error_message, datetime.now().isoformat(), job_id))
            conn.commit()
            self.logger.info(f"Job {job_id} marked as {status}")
