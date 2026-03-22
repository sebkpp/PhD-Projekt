import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import Backend.models

from Backend.db_session import SessionLocal
from Backend.models.trial.trial_slot import TrialSlot

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/testmock/trial_slot.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        slots = json.load(f)

    db = SessionLocal()
    try:
        for s in slots:
            existing = db.query(TrialSlot).filter_by(trial_slot_id=s['trial_slot_id']).first()

            if existing:
                existing.trial_id = s['trial_id']
                existing.slot = s['slot']
                existing.avatar_visibility_id = 1
                print(f"🔄 Updated: TrialSlot {s['trial_slot_id']}")
            else:
                slot = TrialSlot(
                    trial_slot_id=s['trial_slot_id'],
                    trial_id=s['trial_id'],
                    slot=s['slot'],
                    avatar_visibility_id=1,
                )
                db.add(slot)
                print(f"🆕 Inserted: TrialSlot {s['trial_slot_id']}")

        db.commit()
        print("✅ Trial slots imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
