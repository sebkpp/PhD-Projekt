import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Backend.db_session import SessionLocal
from Backend.models.questionnaire import Questionnaire, QuestionnaireItem

QUESTIONNAIRES_FILE = os.path.join(os.path.dirname(__file__), '../data/static/questionnaires.json')


def main():
    with open(QUESTIONNAIRES_FILE, 'r', encoding='utf-8') as f:
        questionnaires = json.load(f)

    db = SessionLocal()
    try:
        for q_def in questionnaires:
            existing = db.query(Questionnaire).filter_by(name=q_def['name']).first()

            if existing:
                existing.scale_type = q_def.get('scale_type', 'slider')
                existing.scale_min = q_def.get('scale_min', 0)
                existing.scale_max = q_def.get('scale_max', 100)
                questionnaire = existing
                print(f"Updated: {q_def['name']} (ID {existing.questionnaire_id})")
            else:
                questionnaire = Questionnaire(
                    name=q_def['name'],
                    scale_type=q_def.get('scale_type', 'slider'),
                    scale_min=q_def.get('scale_min', 0),
                    scale_max=q_def.get('scale_max', 100),
                )
                db.add(questionnaire)
                db.flush()
                print(f"Inserted: {q_def['name']} (ID {questionnaire.questionnaire_id})")

            for item_def in q_def.get('items', []):
                existing_item = db.query(QuestionnaireItem).filter_by(
                    questionnaire_id=questionnaire.questionnaire_id,
                    item_name=item_def['item_name'],
                ).first()

                if existing_item:
                    existing_item.item_label = item_def.get('item_label')
                    existing_item.item_description = item_def.get('item_description')
                    existing_item.min_label = item_def.get('min_label')
                    existing_item.max_label = item_def.get('max_label')
                    existing_item.order_index = item_def.get('order_index', 0)
                    print(f"  Updated item: {item_def['item_name']}")
                else:
                    new_item = QuestionnaireItem(
                        questionnaire_id=questionnaire.questionnaire_id,
                        item_name=item_def['item_name'],
                        item_label=item_def.get('item_label'),
                        item_description=item_def.get('item_description'),
                        min_label=item_def.get('min_label'),
                        max_label=item_def.get('max_label'),
                        order_index=item_def.get('order_index', 0),
                    )
                    db.add(new_item)
                    print(f"  Inserted item: {item_def['item_name']}")

        db.commit()
        print("Questionnaires imported successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
