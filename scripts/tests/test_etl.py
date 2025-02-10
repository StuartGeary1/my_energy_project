# scripts/tests/test_etl.py

import os
import json
import tempfile
from datetime import datetime
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Import functions and models from your ETL and model modules.
import scripts.etl as etl
from scripts.etl import validate_record, process_json_file
from dashboard.models import Base, PresidentialAction

# ------------------------------------------------------------------------------
# Fixture: Create a temporary SQLite database file for testing.
# ------------------------------------------------------------------------------

@pytest.fixture
def test_db(tmp_path, monkeypatch):
    """
    Create a temporary SQLite database file, override the DB_URI in etl, and
    yield a SQLAlchemy session connected to that database.
    """
    # Create a temporary database file
    db_file = tmp_path / "test.db"
    test_db_uri = f"sqlite:///{db_file}"
    # Override the DB_URI in the etl module so that run_etl() and others use it.
    monkeypatch.setattr(etl, "DB_URI", test_db_uri)
    
    # Set up the database engine and session.
    engine = create_engine(test_db_uri)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

# ------------------------------------------------------------------------------
# Test: Schema Validation
# ------------------------------------------------------------------------------

def test_validate_record_valid():
    valid_record = {
        "action_title": "Test Action",
        "action_date": "2020-01-01",
        "source_url": "http://example.com"
    }
    # Expect no exception for a valid record.
    validate_record(valid_record)

def test_validate_record_invalid():
    # Record missing the required "action_date" field.
    invalid_record = {
        "action_title": "Test Action",
        "source_url": "http://example.com"
    }
    with pytest.raises(Exception):
        validate_record(invalid_record)

# ------------------------------------------------------------------------------
# Test: Database Insertion via process_json_file
# ------------------------------------------------------------------------------

def test_process_json_file_insertion(test_db, tmp_path):
    """
    Create a temporary JSON file with a valid record and test that it is inserted
    into the database.
    """
    test_data = [
        {
            "action_title": "Action 1",
            "action_date": "2020-01-01",
            "source_url": "http://example.com/1"
        }
    ]
    json_file = tmp_path / "test_data.json"
    json_file.write_text(json.dumps(test_data))
    
    # Call process_json_file with the temporary JSON file.
    process_json_file(str(json_file), test_db)
    
    # Query the database for the inserted record.
    inserted = test_db.query(PresidentialAction).filter_by(action_title="Action 1").first()
    assert inserted is not None
    assert inserted.action_date == datetime.strptime("2020-01-01", "%Y-%m-%d").date()

def test_duplicate_record(test_db, tmp_path):
    """
    Create a JSON file with duplicate records (same key fields) and verify that
    only one record is inserted.
    """
    test_data = [
        {
            "action_title": "Duplicate Action",
            "action_date": "2020-02-01",
            "source_url": "http://example.com/dup"
        },
        {
            "action_title": "Duplicate Action",
            "action_date": "2020-02-01",
            "source_url": "http://example.com/dup"
        }
    ]
    json_file = tmp_path / "duplicate_data.json"
    json_file.write_text(json.dumps(test_data))
    
    process_json_file(str(json_file), test_db)
    
    # Only one record should be inserted due to the unique hash constraint.
    records = test_db.query(PresidentialAction).filter_by(action_title="Duplicate Action").all()
    assert len(records) == 1

# ------------------------------------------------------------------------------
# Test: Retry Mechanism
# ------------------------------------------------------------------------------

def test_retry_mechanism(monkeypatch, tmp_path, test_db):
    """
    Simulate a failure on the first call to process_json_file, then allow it to
    succeed on a subsequent attempt. Verify that the record is eventually inserted.
    """
    call_count = {"count": 0}
    original_process = etl.process_json_file

    def flaky_process(filepath, session):
        if call_count["count"] < 1:
            call_count["count"] += 1
            raise Exception("Simulated failure")
        else:
            original_process(filepath, session)

    # Override process_json_file with our flaky version.
    monkeypatch.setattr(etl, "process_json_file", flaky_process)

    test_data = [
        {
            "action_title": "Flaky Action",
            "action_date": "2020-03-01",
            "source_url": "http://example.com/flaky"
        }
    ]
    json_file = tmp_path / "flaky_data.json"
    json_file.write_text(json.dumps(test_data))
    
    # Manually implement a retry loop similar to run_etl's logic.
    retries = 0
    success = False
    while retries < etl.MAX_RETRIES:
        try:
            etl.process_json_file(str(json_file), test_db)
            success = True
            break
        except Exception as e:
            retries += 1

    assert success, "Process should eventually succeed after retries"
    
    # Verify the record has been inserted.
    inserted = test_db.query(PresidentialAction).filter_by(action_title="Flaky Action").first()
    assert inserted is not None
