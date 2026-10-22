import sys
import os
import logging
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worker.job_worker import JobWorker

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    parser = argparse.ArgumentParser(description="Devnox AI Hacker OS - Job Worker")
    parser.add_argument("--db-path", default="data/ai_hackeros.db", help="Path to SQLite database")
    parser.add_argument("--poll-interval", type=int, default=5, help="Seconds to wait between polls")
    args = parser.parse_args()

    worker = JobWorker(db_path=args.db_path, poll_interval=args.poll_interval)
    try:
        worker.start()
    except KeyboardInterrupt:
        worker.stop()

if __name__ == "__main__":
    main()
