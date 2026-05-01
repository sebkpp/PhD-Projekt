import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Backend.db_session import SessionLocal
from Backend.models.stimulus import StimulusType

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/static/stimuli_definitions.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        stimuli_data = json.load(f)

    seen = set()
    type_names = []
    for s in stimuli_data:
        if s['type'] not in seen:
            seen.add(s['type'])
            type_names.append(s['type'])

    db = SessionLocal()
    try:
        for type_name in type_names:
            existing = db.query(StimulusType).filter_by(type_name=type_name).first()
            if existing:
                print(f"🔄 Already exists: {type_name}")
            else:
                db.add(StimulusType(type_name=type_name))
                print(f"🆕 Inserted: {type_name}")

        db.commit()
        print("✅ Stimulus types imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
