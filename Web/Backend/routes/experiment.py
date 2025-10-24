from flask import Blueprint, request, jsonify

from Backend.services.experiment_service import create_experiment, get_experiment_by_id, \
    save_experiment_questionnaires, set_experiment_started_at, set_experiment_completed_at
from Backend.db_session import SessionLocal

experiment_bp = Blueprint('experiment', __name__)

@experiment_bp.route('/', methods=['POST'], strict_slashes=False)
def create_experiment_route():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Ungültige JSON-Daten."}), 400

    session = SessionLocal()
    try:
        print("Received data for experiment creation:", data)
        experiment = create_experiment(session, data)
        session.commit()
        return jsonify({"experiment_id": experiment.experiment_id}), 201
    except Exception as e:
        session.rollback()
        print("Fehler beim Anlegen eines Experiments:", e)
        return jsonify({"error": "Interner Serverfehler"}), 500
    finally:
        session.close()


@experiment_bp.route('/<int:experiment_id>', methods=['GET'], strict_slashes=False)
def get_experiment_route(experiment_id):
    session = SessionLocal()
    try:
        experiment = get_experiment_by_id(session, experiment_id)
        if not experiment:
            return jsonify({"error": "Experiment Not Found"}), 404
        return jsonify(experiment.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@experiment_bp.route('/<int:experiment_id>/questionnaires', methods=['PUT'])
def update_linked_questionnaires(experiment_id):
    session = SessionLocal
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({"error": "Expected a list of questionnaire IDs"}), 400

        experiment = get_experiment_by_id(session, experiment_id)
        if not experiment:
            return jsonify({"error": "Experiment not found"}), 404

        save_experiment_questionnaires(session, experiment_id, data)
        session.commit()

        return jsonify({"message": "Questionnaires updated"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()

@experiment_bp.route('/<int:experiment_id>/started', methods=['POST'])
def set_experiment_started(experiment_id):
    session = SessionLocal()
    try:
        set_experiment_started_at(session, experiment_id)
        session.commit()
        return jsonify({"message": "Experiment started_at gesetzt"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@experiment_bp.route('/<int:experiment_id>/completed', methods=['POST'])
def set_experiment_completed(experiment_id):
    session = SessionLocal()
    try:
        set_experiment_completed_at(session, experiment_id)
        session.commit()
        return jsonify({"message": "Experiment completed_at gesetzt"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()