import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import Backend.models

from Backend.db_session import SessionLocal
from Backend.models.study.study_stimuli import StudyStimuli

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/testmock/study_stimuli.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        items = json.load(f)

    db = SessionLocal()
    try:
        for item in items:
            existing = db.query(StudyStimuli).filter_by(
                study_id=item['study_id'],
                stimuli_type_id=item['stimuli_type_id']
            ).first()

            if existing:
                print(f"🔄 Already exists: StudyStimuli study={item['study_id']} type={item['stimuli_type_id']}")
            else:
                ss = StudyStimuli(
                    study_id=item['study_id'],
                    stimuli_type_id=item['stimuli_type_id'],
                )
                db.add(ss)
                print(f"🆕 Inserted: StudyStimuli study={item['study_id']} type={item['stimuli_type_id']}")

        db.commit()
        print("✅ Study stimuli imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
