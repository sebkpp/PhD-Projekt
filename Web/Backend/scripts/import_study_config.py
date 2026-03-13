import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import Backend.models

from Backend.db_session import SessionLocal
from Backend.models.study.study_config import StudyConfig

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/testmock/study_config.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        configs = json.load(f)

    db = SessionLocal()
    try:
        for c in configs:
            existing = db.query(StudyConfig).filter_by(study_config_id=c['study_config_id']).first()

            if existing:
                existing.name = c['name']
                existing.description = c['description']
                existing.principal_investigator = c['principal_investigator']
                existing.study_id = c['study_id']
                existing.trial_number = c['trial_number']
                existing.trials_permuted = c['trials_permuted']
                print(f"🔄 Updated: StudyConfig {c['study_config_id']}")
            else:
                config = StudyConfig(
                    study_config_id=c['study_config_id'],
                    name=c['name'],
                    description=c['description'],
                    principal_investigator=c['principal_investigator'],
                    study_id=c['study_id'],
                    trial_number=c['trial_number'],
                    trials_permuted=c['trials_permuted'],
                )
                db.add(config)
                print(f"🆕 Inserted: StudyConfig {c['study_config_id']}")

        db.commit()
        print("✅ Study configs imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
