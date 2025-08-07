from flask import Blueprint, request, jsonify
from Backend.db_session import SessionLocal
from Backend.services.trial_service import save_trials, get_trials_for_experiment
import traceback

trial_bp = Blueprint('trial', __name__)

@trial_bp.route('/experiments/<int:experiment_id>/trials', methods=['POST'])
def save_trials_route(experiment_id):
    session = SessionLocal()
    try:
        data = request.get_json(force=False, silent=True)  # <-- so wird None zurückgegeben statt Exception
        if data is None:
            return jsonify({"error": "Ungültiges oder fehlendes JSON"}), 400

        trials = data.get("trials")

        if not trials:
            return jsonify({"error": "trials ist erforderlich"}), 400

        result = save_trials(session, experiment_id, trials)
        session.commit()
        return jsonify(result), 201

    except Exception as e:
        session.rollback()
        print("❌ Fehler beim Speichern der Trial-Konfiguration:")
        traceback.print_exc()
        return jsonify({"error": "Ein interner Fehler ist aufgetreten.", "details": str(e)}), 500

    finally:
        session.close()


@trial_bp.route('/experiments/<int:experiment_id>/trials', methods=['GET'])
def get_trials_route(experiment_id):
    session = SessionLocal()
    try:
        trials = get_trials_for_experiment(session, experiment_id)
        return jsonify(trials), 200

    except Exception as e:
        print("❌ Fehler beim Abrufen der Trials:")
        traceback.print_exc()
        return jsonify({"error": "Ein Fehler ist aufgetreten.", "details": str(e)}), 500

    finally:
        session.close()