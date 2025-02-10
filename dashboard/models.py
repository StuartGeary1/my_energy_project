# dashboard/models.py
"""
This module defines the PresidentialAction model.
Changes:
  - Replaced action_date with action_timestamp (a DateTime field) to store full datetime info.
  - Added a new nullable 'theme' column for breakdown by theme.
Reference:
  - SQLAlchemy Datetime: https://docs.sqlalchemy.org/en/14/core/type_basics.html#sqlalchemy.types.DateTime
  - SQLAlchemy UniqueConstraint: https://docs.sqlalchemy.org/en/14/core/constraints.html#sqlalchemy.schema.UniqueConstraint
"""
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import hashlib

Base = declarative_base()

class PresidentialAction(Base):
    __tablename__ = 'presidential_actions'
    
    id = Column(Integer, primary_key=True)
    action_title = Column(String, nullable=False)
    action_timestamp = Column(DateTime, nullable=False)  # Changed from date to full datetime.
    source_url = Column(String, nullable=True)
    theme = Column(String, nullable=True)  # New field for theme breakdown.
    hash_value = Column(String, unique=True, nullable=False)
    
    __table_args__ = (UniqueConstraint('hash_value', name='_hash_uc'), )
    
    def __init__(self, action_title, action_timestamp, source_url=None, theme=None):
        self.action_title = action_title
        # Accept both datetime objects and ISO format strings.
        if isinstance(action_timestamp, str):
            self.action_timestamp = datetime.fromisoformat(action_timestamp)
        else:
            self.action_timestamp = action_timestamp
        self.source_url = source_url
        self.theme = theme
        # Compute a unique hash from key fields.
        hash_input = f"{action_title}{self.action_timestamp}{source_url}".encode('utf-8')
        self.hash_value = hashlib.sha256(hash_input).hexdigest()
