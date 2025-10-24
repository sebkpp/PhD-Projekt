from flask import Blueprint, request, jsonify

from Backend.db_session import SessionLocal
from Backend.services.trial_service import save_trials, get_trials_for_experiment, finish_trial, \
    save_experiment_questionnaires, get_trial, start_trial, get_participants_for_trial
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
        selected_questionnaires_raw = data.get("questionnaires", [])
        selected_questionnaires = [q["questionnaire_id"] for q in selected_questionnaires_raw]

        if not trials:
            return jsonify({"error": "trials ist erforderlich"}), 400

        if selected_questionnaires is None:
            return jsonify({"error": "selectedQuestionnaires ist erforderlich"}), 400

        result = save_trials(session, experiment_id, trials, selected_questionnaires)

        save_experiment_questionnaires(session, experiment_id, selected_questionnaires)

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
        print("Get Trials for experiment", experiment_id, ":", trials)
        return jsonify(trials), 200

    except Exception as e:
        print("❌ Fehler beim Abrufen der Trials:")
        traceback.print_exc()
        return jsonify({"error": "Ein Fehler ist aufgetreten.", "details": str(e)}), 500

    finally:
        session.close()

current_trial_id = None

@trial_bp.route('/trial/<int:trial_id>/start', methods=['POST'])
def start_trial_route(trial_id):
    session = SessionLocal()
    global current_trial_id
    try:
        print("Trial started:", trial_id)
        start_trial(session, trial_id)
        current_trial_id = trial_id
        # send_start_signal_to_unity(trial_id)
        session.commit()
        return jsonify({"message": "Trial started"}), 200
    except Exception as e:
        print("Fehler beim Starten des Trials:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@trial_bp.route('/trial/<int:trial_id>/end', methods=['POST'])
def end_trial(trial_id):
    session = SessionLocal()
    global current_trial_id
    try:
        print("Trial ended:", trial_id)
        finish_trial(session, trial_id)
        current_trial_id = None
        session.commit()
        return jsonify({"status": "ok", "message": f"Trial {trial_id} marked as finished"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

@trial_bp.route('/trial/current_trial', methods=['GET'])
def get_current_trial():
    return jsonify(trial_id=current_trial_id)

@trial_bp.route('/trial/<int:trial_id>', methods=['GET'])
def get_trial_route(trial_id):
    session = SessionLocal()
    try:
        trial = get_trial(session, trial_id)
        return jsonify(trial.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

@trial_bp.route('/trial/<int:trial_id>/participants', methods=['GET'])
def get_trial_participants(trial_id):
    session = SessionLocal()
    try:
        participants = get_participants_for_trial(session, trial_id)
        return jsonify([p.to_dict() for p in participants]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        session.close()

