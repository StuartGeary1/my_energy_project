# scripts/check_data.py
from dashboard.business_logic import get_db_session
from dashboard.models import PresidentialAction

def check_data():
    session = get_db_session()
    count = session.query(PresidentialAction).count()
    print(f"Number of records in presidential_actions: {count}")
    session.close()

if __name__ == '__main__':
    check_data()
