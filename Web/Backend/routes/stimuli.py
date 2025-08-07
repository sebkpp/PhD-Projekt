from flask import Blueprint, jsonify
from Backend.db_session import SessionLocal
from Backend.services.stimuli_service import get_all_stimuli
import traceback

stimuli_bp = Blueprint('stimuli', __name__)

@stimuli_bp.route('/stimuli', methods=['GET'])
def get_stimuli():
    session = SessionLocal()
    try:
        data = get_all_stimuli(session)
        return jsonify(data), 200
    except Exception as e:
        print("❌ Fehler beim Laden der Stimuli:")
        traceback.print_exc()
        return jsonify({"error": "Interner Serverfehler", "details": str(e)}), 500
    finally:
        session.close()