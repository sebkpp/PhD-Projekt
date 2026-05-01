import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import Backend.models

from Backend.db_session import SessionLocal
from Backend.models.trial.trial_participant_slot import TrialParticipantSlot

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/testmock/trial_participant_slot.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        assignments = json.load(f)

    db = SessionLocal()
    try:
        for a in assignments:
            existing = db.query(TrialParticipantSlot).filter_by(
                trial_slot_id=a['trial_slot_id'],
                participant_id=a['participant_id']
            ).first()

            if existing:
                print(f"🔄 Already exists: TrialParticipantSlot slot={a['trial_slot_id']} participant={a['participant_id']}")
            else:
                assignment = TrialParticipantSlot(
                    trial_slot_id=a['trial_slot_id'],
                    participant_id=a['participant_id'],
                )
                db.add(assignment)
                print(f"🆕 Inserted: TrialParticipantSlot slot={a['trial_slot_id']} participant={a['participant_id']}")

        db.commit()
        print("✅ Trial participant slots imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
