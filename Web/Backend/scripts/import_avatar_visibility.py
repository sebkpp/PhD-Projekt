import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Backend.db_session import SessionLocal
from Backend.models.avatar_visibility import AvatarVisibility

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/static/avatar_visibility.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        visibilities = json.load(f)

    db = SessionLocal()
    try:
        for item in visibilities:
            existing = db.query(AvatarVisibility).filter_by(
                avatar_visibility_name=item['name']
            ).first()

            if existing:
                existing.label = item['label']
                print(f"🔄 Updated: {item['name']}")
            else:
                av = AvatarVisibility(
                    avatar_visibility_name=item['name'],
                    label=item['label'],
                )
                db.add(av)
                print(f"🆕 Inserted: {item['name']}")

        db.commit()
        print("✅ Avatar visibilities imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
