import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import Backend.models

from Backend.db_session import SessionLocal
from Backend.models.questionnaire import QuestionnaireResponse

DATA_FILE = os.path.join(os.path.dirname(__file__), '../data/testmock/questionnaire_response.json')


def main():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        responses = json.load(f)

    db = SessionLocal()
    try:
        for r in responses:
            existing = db.query(QuestionnaireResponse).filter_by(
                questionnaire_response_id=r['questionnaire_response_id']
            ).first()

            if existing:
                existing.trial_id = r['trial_id']
                existing.participant_id = r['participant_id']
                existing.questionnaire_item_id = r['questionnaire_item_id']
                existing.response_value = r['response_value']
                print(f"🔄 Updated: QuestionnaireResponse {r['questionnaire_response_id']}")
            else:
                response = QuestionnaireResponse(
                    questionnaire_response_id=r['questionnaire_response_id'],
                    trial_id=r['trial_id'],
                    participant_id=r['participant_id'],
                    questionnaire_item_id=r['questionnaire_item_id'],
                    response_value=r['response_value'],
                )
                db.add(response)
                print(f"🆕 Inserted: QuestionnaireResponse {r['questionnaire_response_id']}")

        db.commit()
        print("✅ Questionnaire responses imported.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == '__main__':
    main()
