import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import Backend.models

from Backend.db_session import SessionLocal
from Backend.models.trial.trial import Trial

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/testmock/trial.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        trials = json.load(f)

    db = SessionLocal()
    try:
        for t in trials:
            existing = db.query(Trial).filter_by(trial_id=t['trial_id']).first()

            if existing:
                existing.experiment_id = t['experiment_id']
                existing.trial_number = t['trial_number']
                existing.is_finished = t['is_finished']
                print(f"🔄 Updated: Trial {t['trial_id']}")
            else:
                trial = Trial(
                    trial_id=t['trial_id'],
                    experiment_id=t['experiment_id'],
                    trial_number=t['trial_number'],
                    is_finished=t['is_finished'],
                )
                db.add(trial)
                print(f"🆕 Inserted: Trial {t['trial_id']}")

        db.commit()
        print("✅ Trials imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
