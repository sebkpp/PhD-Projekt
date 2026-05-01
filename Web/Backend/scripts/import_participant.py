import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import Backend.models

from Backend.db_session import SessionLocal
from Backend.models.participant import Participant

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/testmock/participant.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        participants = json.load(f)

    db = SessionLocal()
    try:
        for p in participants:
            existing = db.query(Participant).filter_by(participant_id=p['participant_id']).first()

            if existing:
                existing.age = p['age']
                existing.gender = p['gender']
                existing.handedness = p['handedness']
                print(f"🔄 Updated: Participant {p['participant_id']}")
            else:
                participant = Participant(
                    participant_id=p['participant_id'],
                    age=p['age'],
                    gender=p['gender'],
                    handedness=p['handedness'],
                )
                db.add(participant)
                print(f"🆕 Inserted: Participant {p['participant_id']}")

        db.commit()
        print("✅ Participants imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
