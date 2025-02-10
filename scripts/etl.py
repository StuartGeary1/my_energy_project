# scripts/etl.py

import json
import glob
import logging
import os
import time
from datetime import datetime

from jsonschema import validate, ValidationError

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

# Import configuration and models
from config.config import DB_URI  # Example: DB_URI = 'sqlite:///data/presidential_actions.db'
from dashboard.models import Base, PresidentialAction

# Set up logging for the ETL process
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the JSON schema for a presidential action record.
PRESIDENTIAL_ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "action_title": {"type": "string"},
        "action_date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},  # YYYY-MM-DD format
        "source_url": {"type": "string", "format": "uri"}
    },
    "required": ["action_title", "action_date"]
}

# Retry mechanism parameters
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def validate_record(record):
    """
    Validate a record against the predefined JSON schema.
    Raises a ValidationError if the record does not conform.
    """
    try:
        validate(instance=record, schema=PRESIDENTIAL_ACTION_SCHEMA)
    except ValidationError as e:
        logger.error(f"Record validation error: {e.message} | Record: {record}")
        raise

def process_json_file(filepath, session):
    """
    Process a single JSON file:
      - Load the JSON data.
      - Validate each record.
      - Convert and insert the record into the database.
    """
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
    except Exception as e:
        logger.error(f"Failed to load JSON file {filepath}: {e}")
        return

    if not isinstance(data, list):
        logger.error(f"Data in {filepath} is not a list of records.")
        return

    for record in data:
        try:
            # Validate the record structure
            validate_record(record)
            
            # Convert action_date from string to a date object
            action_date = datetime.strptime(record['action_date'], "%Y-%m-%d").date()
            
            # Create an instance of PresidentialAction
            action = PresidentialAction(
                action_title=record['action_title'],
                action_date=action_date,
                source_url=record.get('source_url')
            )
            
            # Attempt to add and commit the record
            session.add(action)
            session.commit()
            logger.info(f"Inserted: {action.action_title} on {action.action_date}")
        
        except IntegrityError:
            session.rollback()
            logger.warning(f"Duplicate record skipped: {record}")
        
        except Exception as e:
            session.rollback()
            logger.error(f"Error processing record {record}: {e}")

def run_etl():
    """
    Run the ETL process:
      - Set up the database and session.
      - Process all JSON files in the data directory with a retry mechanism.
    """
    # Set up SQLAlchemy engine and session
    engine = create_engine(DB_URI)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Find JSON files in the data directory
    json_files = glob.glob(os.path.join('data', '*.json'))
    
    for filepath in json_files:
        retries = 0
        while retries < MAX_RETRIES:
            try:
                logger.info(f"Processing file: {filepath}")
                process_json_file(filepath, session)
                break  # Successfully processed the file; break out of the retry loop.
            except Exception as e:
                retries += 1
                logger.error(f"Error processing {filepath}: {e} | Attempt {retries}/{MAX_RETRIES}")
                if retries < MAX_RETRIES:
                    logger.info(f"Retrying {filepath} in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"Max retries reached for {filepath}. Skipping file.")
    
    session.close()

if __name__ == '__main__':
    run_etl()
