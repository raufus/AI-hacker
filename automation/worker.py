import time
import logging
import sqlite3
import json
import os
import sys

# Add project root to sys.path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import DatabaseManager
from modules.scanning import NetworkScanner, WebScanner

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Worker")

class Worker:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.running = False

    def start(self):
        self.running = True
        logger.info("Worker started, polling for queued jobs...")
        while self.running:
            try:
                self.poll_and_execute()
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
            time.sleep(3) # Polling interval

    def stop(self):
        self.running = False
        logger.info("Worker stopping...")

    def poll_and_execute(self):
        job = self.db.claim_job()
        if not job:
            return

        job_id, module_name, target, input_data = job
        logger.info(f"Claimed job {job_id} for module {module_name} on target {target}")

        try:
            # Note: claim_job sets status to 'running'

            scanner = None
            if module_name == 'network_discovery':
                scanner = NetworkScanner(target=target)
            elif module_name == 'web_scanner':
                scanner = WebScanner(target=target)
            else:
                raise ValueError(f"Unknown module: {module_name}")

            logger.info(f"Executing job {job_id}...")
            # We assume these scanner modules have a scan() method that returns results or True/False
            # For this MVP worker, we'll try to call scan() and save results
            results = {}
            if hasattr(scanner, 'scan'):
                # Handle async scanning or sync scanning based on what is available
                import asyncio
                if asyncio.iscoroutinefunction(scanner.scan):
                    loop = asyncio.get_event_loop()
                    results = loop.run_until_complete(scanner.scan())
                else:
                    results = scanner.scan()
            else:
                raise AttributeError(f"Module {module_name} does not have a scan() method.")

            logger.info(f"Job {job_id} completed successfully.")
            self.db.update_job_result(job_id, "completed", results)

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            self.db.update_job_result(job_id, "failed", {"error": str(e)})

if __name__ == "__main__":
    db = DatabaseManager()
    worker = Worker(db)
    try:
        worker.start()
    except KeyboardInterrupt:
        worker.stop()
