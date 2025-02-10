# dashboard/business_logic.py
"""
This module contains functions to query and aggregate the presidential action data.
References:
  - SQLAlchemy extract(): https://docs.sqlalchemy.org/en/14/core/expression_api.html#sqlalchemy.sql.expression.extract
  - Flask logging: https://flask.palletsprojects.com/en/2.2.x/logging/
"""
from sqlalchemy import create_engine, func, extract
from sqlalchemy.orm import sessionmaker
from config.config import DB_URI
from dashboard.models import PresidentialAction
import logging

logger = logging.getLogger(__name__)

def get_db_session():
    engine = create_engine(DB_URI)
    Session = sessionmaker(bind=engine)
    return Session()

def get_daily_counts():
    """Return daily counts deduplicated via the unique hash."""
    session = get_db_session()
    try:
        # Group by the DATE portion of the full timestamp.
        results = (
            session.query(
                func.date(PresidentialAction.action_timestamp).label('date'),
                func.count(PresidentialAction.id).label('count')
            )
            .group_by(func.date(PresidentialAction.action_timestamp))
            .order_by(func.date(PresidentialAction.action_timestamp))
            .all()
        )
        return results
    except Exception as e:
        logger.error("Error fetching daily counts: %s", e)
        return []
    finally:
        session.close()

def get_actions_by_theme():
    """Return counts grouped by theme."""
    session = get_db_session()
    try:
        results = (
            session.query(
                PresidentialAction.theme,
                func.count(PresidentialAction.id).label('count')
            )
            .group_by(PresidentialAction.theme)
            .order_by(PresidentialAction.theme)
            .all()
        )
        return results
    except Exception as e:
        logger.error("Error fetching actions by theme: %s", e)
        return []
    finally:
        session.close()

def get_actions_by_hour():
    """Return counts aggregated by hour extracted from the timestamp."""
    session = get_db_session()
    try:
        results = (
            session.query(
                extract('hour', PresidentialAction.action_timestamp).label('hour'),
                func.count(PresidentialAction.id).label('count')
            )
            .group_by('hour')
            .order_by('hour')
            .all()
        )
        return results
    except Exception as e:
        logger.error("Error fetching actions by hour: %s", e)
        return []
    finally:
        session.close()

def get_actions_by_hour_full():
    """
    Wraps get_actions_by_hour() to always return a complete set for 24 hours.
    This ensures our chart always shows hours 0-23.
    """
    raw_hour_data = get_actions_by_hour()  # List of tuples: (hour, count)
    hour_counts = {hour: 0 for hour in range(24)}  # Pre-fill all 24 hours with 0.
    for hour, count in raw_hour_data:
        hour_counts[int(hour)] = count
    hours = sorted(hour_counts.keys())
    counts = [hour_counts[h] for h in hours]
    return hours, counts
