# scripts/init_db.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# scripts/init_db.py
"""
This script initializes (or resets) the database.
WARNING: It drops all existing tables.
Reference: SQLAlchemy metadata API - https://docs.sqlalchemy.org/en/14/core/metadata.html
"""
from sqlalchemy import create_engine
from dashboard.models import Base
from config.config import DB_URI

def init_db():
    engine = create_engine(DB_URI)
    # Drop all tables and recreate them to reflect model changes.
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Database initialized.")

if __name__ == "__main__":
    init_db()
