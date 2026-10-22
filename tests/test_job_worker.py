import unittest
import os
import sqlite3
from database.database import DatabaseManager
from worker.job_worker import JobWorker

class TestJobWorker(unittest.TestCase):
    def setUp(self):
        self.db_path = "data/test_worker.db"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.db = DatabaseManager(self.db_path)
        self.worker = JobWorker(db_path=self.db_path, poll_interval=1)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_job_claim_and_authorization(self):
        eng_id = self.db.create_engagement("Test Eng")
        # Unauthorized target
        t1_id = self.db.add_target(eng_id, "127.0.0.1", authorized=False)
        job_id = self.db.create_job(eng_id, t1_id, "Network Scanner")

        job = self.worker._claim_next_job()
        self.assertIsNotNone(job)
        self.assertEqual(job['id'], job_id)

        # Execute should fail due to authorization
        self.worker._execute_job(job)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, error_message FROM jobs WHERE id = ?", (job_id,))
            status, err = cursor.fetchone()
            self.assertEqual(status, "failed")
            self.assertIn("not authorized", err)

    def test_job_execution_authorized(self):
        eng_id = self.db.create_engagement("Test Eng 2")
        # Authorized target
        t2_id = self.db.add_target(eng_id, "127.0.0.1", authorized=True)
        job_id = self.db.create_job(eng_id, t2_id, "Web Scanner")

        job = self.worker._claim_next_job()
        self.worker._execute_job(job)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, output_data FROM jobs WHERE id = ?", (job_id,))
            status, out = cursor.fetchone()
            self.assertEqual(status, "completed")
            self.assertIsNotNone(out)

if __name__ == '__main__':
    unittest.main()
