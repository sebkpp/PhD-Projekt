import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Backend.db_session import SessionLocal
from Backend.models.eyetracking import AreaOfInterest

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/static/aoi_definitions.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        aois = json.load(f)

    db = SessionLocal()
    try:
        for aoi in aois:
            existing = db.query(AreaOfInterest).filter_by(aoi=aoi['aoi']).first()

            if existing:
                existing.label = aoi['label']
                print(f"🔄 Updated: {aoi['aoi']}")
            else:
                new_aoi = AreaOfInterest(
                    aoi=aoi['aoi'],
                    label=aoi['label'],
                )
                db.add(new_aoi)
                print(f"🆕 Inserted: {aoi['aoi']}")

        db.commit()
        print("✅ AOIs imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
