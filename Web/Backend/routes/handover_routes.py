from flask import Blueprint, request, jsonify
from Backend.db_session import SessionLocal
from Backend.services.handover_service import save_handover, get_handovers_for_trial, get_handovers_for_experiment
import traceback

handover_bp = Blueprint("handover", __name__)

@handover_bp.route('/trials/<int:trial_id>/handovers', methods=['GET'])
def get_handovers_route(trial_id):
    session = SessionLocal()
    try:
        handovers = get_handovers_for_trial(session, trial_id)
        handover_list = [h.to_dict() for h in handovers]
        return jsonify(handover_list), 200

    except Exception as e:
        print("❌ Fehler beim Abrufen der Handovers:")
        traceback.print_exc()
        return jsonify({"error": "Ein Fehler ist aufgetreten.", "details": str(e)}), 500

    finally:
        session.close()

@handover_bp.route('/experiments/<int:experiment_id>/handovers', methods=['GET'])
def get_handovers_for_experiment_route(experiment_id):
    session = SessionLocal()
    try:
        handovers = get_handovers_for_experiment(session, experiment_id)
        handover_list = [h.to_dict() for h in handovers]
        return jsonify(handover_list), 200
    except Exception as e:
        print("❌ Fehler beim Abrufen der Handovers für Experiment:")
        traceback.print_exc()
        return jsonify({"error": "Ein Fehler ist aufgetreten.", "details": str(e)}), 500
    finally:
        session.close()

@handover_bp.route('/trials/<int:trial_id>/handovers', methods=['POST'])
def save_handover_route(trial_id):
    session = SessionLocal()
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "Kein JSON gesendet"}), 400

        print("Received handover data:", data)
        # trial_id aus URL übernehmen, Sicherheit
        data['trial_id'] = trial_id

        new_handover = save_handover(session, data)
        session.commit()
        return jsonify({"message": "Handover gespeichert", "handover_id": new_handover.handover_id}), 201

    except Exception as e:
        session.rollback()
        print("Fehler beim Speichern des Handovers:")
        return jsonify({"error": "Ein interner Fehler ist aufgetreten.", "details": str(e)}), 500

    finally:
        session.close()
