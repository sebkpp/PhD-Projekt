import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import Backend.models

from Backend.db_session import SessionLocal
from Backend.models.experiment import Experiment

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/testmock/experiment_1.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        experiments = json.load(f)

    db = SessionLocal()
    try:
        for e in experiments:
            existing = db.query(Experiment).filter_by(experiment_id=e['experiment_id']).first()

            if existing:
                existing.study_id = e['study_id']
                existing.description = e['description']
                existing.created_at = e['created_at']
                existing.started_at = e['started_at']
                existing.completed_at = e['completed_at']
                existing.researcher = e['researcher']
                print(f"🔄 Updated: Experiment {e['experiment_id']}")
            else:
                experiment = Experiment(
                    experiment_id=e['experiment_id'],
                    study_id=e['study_id'],
                    description=e['description'],
                    created_at=e['created_at'],
                    started_at=e['started_at'],
                    completed_at=e['completed_at'],
                    researcher=e['researcher'],
                )
                db.add(experiment)
                print(f"🆕 Inserted: Experiment {e['experiment_id']}")

        db.commit()
        print("✅ Experiments imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
