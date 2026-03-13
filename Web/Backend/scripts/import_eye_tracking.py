import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import Backend.models

from Backend.db_session import SessionLocal
from Backend.models.eyetracking import EyeTracking

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/testmock/eye_tracking.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        records = json.load(f)

    db = SessionLocal()
    try:
        for r in records:
            existing = db.query(EyeTracking).filter_by(eye_tracking_id=r['eye_tracking_id']).first()

            if existing:
                existing.participant_id = r['participant_id']
                existing.hanover_id = r['hanover_id']
                existing.aoi_id = r['aoi_id']
                existing.starttime = r['starttime']
                existing.endtime = r['endtime']
                existing.duration = r['duration']
                print(f"🔄 Updated: EyeTracking {r['eye_tracking_id']}")
            else:
                et = EyeTracking(
                    eye_tracking_id=r['eye_tracking_id'],
                    participant_id=r['participant_id'],
                    hanover_id=r['hanover_id'],
                    aoi_id=r['aoi_id'],
                    starttime=r['starttime'],
                    endtime=r['endtime'],
                    duration=r['duration'],
                )
                db.add(et)
                print(f"🆕 Inserted: EyeTracking {r['eye_tracking_id']}")

        db.commit()
        print("✅ Eye tracking data imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
