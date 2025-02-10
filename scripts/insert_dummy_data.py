# scripts/insert_dummy_data.py

from datetime import date
from dashboard.business_logic import get_db_session
from dashboard.models import PresidentialAction

def insert_dummy_data():
    session = get_db_session()
    try:
        # Define some dummy records.
        dummy_records = [
            {
                "action_title": "Action One",
                "action_date": date(2025, 2, 8),
                "source_url": "http://example.com/one"
            },
            {
                "action_title": "Action Two",
                "action_date": date(2025, 2, 9),
                "source_url": "http://example.com/two"
            },
            {
                "action_title": "Action Three",
                "action_date": date(2025, 2, 8),
                "source_url": "http://example.com/three"
            },
        ]
        
        for record in dummy_records:
            # Create a new PresidentialAction instance.
            pa = PresidentialAction(
                action_title=record["action_title"],
                action_date=record["action_date"],
                source_url=record["source_url"]
            )
            session.add(pa)
        
        session.commit()
        print("Dummy data inserted successfully.")
    except Exception as e:
        session.rollback()
        print("Error inserting dummy data:", e)
    finally:
        session.close()

if __name__ == '__main__':
    insert_dummy_data()
