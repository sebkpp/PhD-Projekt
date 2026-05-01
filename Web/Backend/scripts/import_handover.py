import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import Backend.models

from Backend.db_session import SessionLocal
from Backend.models.handover import Handover

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/testmock/handover.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        handovers = json.load(f)

    db = SessionLocal()
    try:
        for h in handovers:
            existing = db.query(Handover).filter_by(handover_id=h['handover_id']).first()

            if existing:
                existing.trial_id = h['trial_id']
                existing.giver = h['giver']
                existing.receiver = h['receiver']
                existing.grasped_object = h['grasped_object']
                existing.giver_grasped_object = h['giver_grasped_object']
                existing.giver_released_object = h['giver_released_object']
                existing.receiver_touched_object = h['receiver_touched_object']
                existing.receiver_grasped_object = h['receiver_grasped_object']
                print(f"🔄 Updated: Handover {h['handover_id']}")
            else:
                handover = Handover(
                    handover_id=h['handover_id'],
                    trial_id=h['trial_id'],
                    giver=h['giver'],
                    receiver=h['receiver'],
                    grasped_object=h['grasped_object'],
                    giver_grasped_object=h['giver_grasped_object'],
                    giver_released_object=h['giver_released_object'],
                    receiver_touched_object=h['receiver_touched_object'],
                    receiver_grasped_object=h['receiver_grasped_object'],
                )
                db.add(handover)
                print(f"🆕 Inserted: Handover {h['handover_id']}")

        db.commit()
        print("✅ Handovers imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
