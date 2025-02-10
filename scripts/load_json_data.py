# scripts/load_json_data.py
"""
This script loads JSON data into the SQLite database.
Changes:
  - Uses the full datetime from the JSON (action_timestamp or action_date) via datetime.fromisoformat.
  - Optionally loads a 'theme' field.
Reference:
  - Python datetime.fromisoformat: https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
"""
import json
import os
import sys
from datetime import datetime
from dashboard.models import PresidentialAction, Base
from config.config import DB_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def load_json_data(json_file_path):
    engine = create_engine(DB_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    for record in data:
        action_title = record.get('action_title')
        # Use 'action_timestamp' if available, otherwise fallback to 'action_date'
        action_timestamp_str = record.get('action_timestamp') or record.get('action_date')
        if not action_timestamp_str:
            continue
        try:
            action_timestamp = datetime.fromisoformat(action_timestamp_str)
        except Exception as e:
            print(f"Skipping record with invalid datetime format: {action_timestamp_str}")
            continue
        
        source_url = record.get('source_url')
        theme = record.get('theme')  # New field; may be None.
        
        action = PresidentialAction(action_title, action_timestamp, source_url, theme)
        try:
            session.add(action)
            session.commit()
            print(f"Loaded record: {action_title} at {action_timestamp}")
        except Exception as e:
            session.rollback()
            print(f"Skipped duplicate or error for record: {action_title} at {action_timestamp}")
    
    session.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python load_json_data.py <path_to_json>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    if not os.path.exists(json_file_path):
        print(f"File not found: {json_file_path}")
        sys.exit(1)
    
    load_json_data(json_file_path)
