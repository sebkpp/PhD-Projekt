import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import Backend.models

from Backend.db_session import SessionLocal
from Backend.models.study.study import Study

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/testmock/study.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        studies = json.load(f)

    db = SessionLocal()
    try:
        for s in studies:
            existing = db.query(Study).filter_by(study_id=s['study_id']).first()

            if existing:
                existing.created_at = s['created_at']
                existing.started_at = s['started_at']
                existing.ended_at = s['ended_at']
                existing.status = s['status']
                print(f"🔄 Updated: Study {s['study_id']}")
            else:
                study = Study(
                    study_id=s['study_id'],
                    created_at=s['created_at'],
                    started_at=s['started_at'],
                    ended_at=s['ended_at'],
                    status=s['status'],
                )
                db.add(study)
                print(f"🆕 Inserted: Study {s['study_id']}")

        db.commit()
        print("✅ Studies imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
