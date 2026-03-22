import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import Backend.models

from Backend.db_session import SessionLocal
from Backend.models.trial.trial_slot_stimulus import TrialSlotStimulus

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/testmock/trial_slot_stimulus.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        items = json.load(f)

    db = SessionLocal()
    try:
        for item in items:
            existing = db.query(TrialSlotStimulus).filter_by(
                trial_slot_id=item['trial_slot_id'],
                stimulus_id=item['stimulus_id']
            ).first()

            if existing:
                print(f"🔄 Already exists: TrialSlotStimulus slot={item['trial_slot_id']} stimulus={item['stimulus_id']}")
            else:
                tss = TrialSlotStimulus(
                    trial_slot_id=item['trial_slot_id'],
                    stimulus_id=item['stimulus_id'],
                )
                db.add(tss)
                print(f"🆕 Inserted: TrialSlotStimulus slot={item['trial_slot_id']} stimulus={item['stimulus_id']}")

        db.commit()
        print("✅ Trial slot stimuli imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
