from flask import Blueprint, request, jsonify
from Backend.models.experiment import Experiment
from Backend.utils.validation import validate_experiment_data
from Backend.db_session import SessionLocal

experiment_bp = Blueprint('experiment', __name__)

@experiment_bp.route('/', methods=['POST'], strict_slashes=False)
def create_experiment():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Ungültige JSON-Daten."}), 400

    errors = validate_experiment_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    session = SessionLocal()
    try:
        experiment = Experiment(
            name=data["name"],
            description=data.get("description"),
            researcher=data.get("researcher")
        )
        session.add(experiment)
        session.commit()
        session.refresh(experiment)
        return jsonify({"experiment_id": experiment.experiment_id}), 201
    except Exception as e:
        session.rollback()
        print("Fehler beim Anlegen eines Experiments:", e)
        return jsonify({"error": "Interner Serverfehler"}), 500
    finally:
        session.close()
