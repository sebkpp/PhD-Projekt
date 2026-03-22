import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import Backend.models

from Backend.db_session import SessionLocal
from Backend.models.study.study_questionnaire import StudyQuestionnaire

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/testmock/study_questionnaire.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        items = json.load(f)

    db = SessionLocal()
    try:
        for item in items:
            existing = db.query(StudyQuestionnaire).filter_by(
                study_id=item['study_id'],
                questionnaire_id=item['questionnaire_id']
            ).first()

            if existing:
                existing.order_index = item['order_index']
                existing.trigger_timing = item['trigger_timing']
                print(f"🔄 Updated: StudyQuestionnaire study={item['study_id']} questionnaire={item['questionnaire_id']}")
            else:
                sq = StudyQuestionnaire(
                    study_id=item['study_id'],
                    questionnaire_id=item['questionnaire_id'],
                    order_index=item['order_index'],
                    trigger_timing=item['trigger_timing'],
                )
                db.add(sq)
                print(f"🆕 Inserted: StudyQuestionnaire study={item['study_id']} questionnaire={item['questionnaire_id']}")

        db.commit()
        print("✅ Study questionnaires imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
