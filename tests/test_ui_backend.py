import pytest
import sqlite3
import os
from database.database import DatabaseManager

@pytest.fixture
def temp_db():
    db_path = "tests/temp_test.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = DatabaseManager(db_path)
    yield db
    if os.path.exists(db_path):
        os.remove(db_path)

def test_database_job_lifecycle(temp_db):
    # 1. Create dependencies
    engagement_id = temp_db.create_engagement("Test Engagement", "Desc")
    target_id = temp_db.add_target(engagement_id, "127.0.0.1", "ip", authorized=True)

    # 2. Create job
    job_id = temp_db.create_job(engagement_id, target_id, "network_discovery", {"port": 80})

    # Verify job is queued
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM jobs WHERE id = ?", (job_id,))
        assert cursor.fetchone()[0] == 'queued'

    # 3. Claim job
    claimed_job = temp_db.claim_job()
    assert claimed_job is not None
    claimed_id, module, target, input_data = claimed_job
    assert claimed_id == job_id
    assert module == "network_discovery"
    assert target == "127.0.0.1"

    # Verify status changed to running
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM jobs WHERE id = ?", (job_id,))
        assert cursor.fetchone()[0] == 'running'

    # Claiming again should yield nothing
    assert temp_db.claim_job() is None

    # 4. Update status and result via update_job_result
    fake_results = {"vulnerabilities": [{"name": "Test Vuln", "severity": "high"}]}
    temp_db.update_job_result(job_id, 'completed', fake_results)

    # Verify status and output data
    with sqlite3.connect(temp_db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT status, output_data FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        assert row[0] == 'completed'
        assert '"Test Vuln"' in row[1]

        # Verify findings were created
        cursor.execute("SELECT COUNT(*) FROM scan_results WHERE target_id = ?", (target_id,))
        assert cursor.fetchone()[0] == 1

        cursor.execute("SELECT COUNT(*) FROM vulnerabilities")
        assert cursor.fetchone()[0] == 1

def test_authorization_and_validation(temp_db):
    engagement_id = temp_db.create_engagement("Valid", "Desc")

    # 1. Invalid target inputs
    with pytest.raises(ValueError, match="Invalid target format"):
        temp_db.add_target(engagement_id, "", "ip")

    with pytest.raises(ValueError, match="Invalid target format"):
        temp_db.add_target(engagement_id, "ab", "ip")

    # 2. Invalid engagement
    with pytest.raises(ValueError, match="Engagement does not exist"):
        temp_db.add_target(999, "127.0.0.1", "ip")

    # 3. Add valid unauthorized target
    unauth_target_id = temp_db.add_target(engagement_id, "127.0.0.2", "ip", authorized=False)

    # 4. Try creating job for unauthorized target
    with pytest.raises(ValueError, match="Cannot create job for unauthorized target"):
        temp_db.create_job(engagement_id, unauth_target_id, "network_discovery")

    # 5. Try creating job for wrong engagement
    other_engagement_id = temp_db.create_engagement("Other", "Desc")
    auth_target_id = temp_db.add_target(other_engagement_id, "127.0.0.3", "ip", authorized=True)

    with pytest.raises(ValueError, match="Target does not belong to this engagement"):
        temp_db.create_job(engagement_id, auth_target_id, "network_discovery")
