from flask import Blueprint, request, jsonify
from Backend.services.participant_service import (
    register_participant,
    submit_participant_to_slot,
    get_submission_status
)
from Backend.services.connection_service import (
    update_heartbeat,
    get_connection_status,
    player_joined
)
from Backend.db_session import SessionLocal

participant_bp = Blueprint('participant', __name__, url_prefix='/api/participants')

@participant_bp.route("/join", methods=["POST"])
def player_join():
    data = request.get_json()
    player_id = data.get("player_id")
    if not player_joined(player_id):
        return jsonify({"status": "error", "message": "Ungültige player_id"}), 400

    return jsonify({"status": "joined", "player_id": player_id})


@participant_bp.route("/heartbeat", methods=["POST"])
def player_heartbeat():
    player_id = request.json.get("player_id")
    if not update_heartbeat(player_id):
        return jsonify({"status": "error", "message": "Ungültige player_id"}), 400
    return jsonify({"status": "heartbeat", "player_id": player_id})

@participant_bp.route("/connection_status", methods=["GET"])
def connection_status():
    status = get_connection_status()
    return jsonify(status)


@participant_bp.route('/', methods=['POST'], strict_slashes=False)
def register_participant_route():
    data = request.get_json()
    age = data.get("age")
    gender = data.get("gender")
    handedness = data.get("handedness")

    if not age or not gender or not handedness:
        return jsonify({"error": "Unvollständige Daten"}), 400

    db = SessionLocal()
    try:
        participant = register_participant(db, age, gender, handedness)
        db.commit()
        return jsonify({"participant_id": participant.participant_id}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@participant_bp.route("/submit", methods=["POST"])
def set_submit_status():
    data = request.get_json()
    experiment_id = data.get("experiment_id")
    slot = data.get("slot")
    participant_id = data.get("participant_id")

    try:
        submit_participant_to_slot(experiment_id, slot, participant_id)
        return jsonify({"status": "ok"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@participant_bp.route("/status/<int:slot>", methods=["GET"])
def get_submit_status(slot):
    experiment_id = request.args.get("experiment_id")

    try:
        status = get_submission_status(experiment_id, slot)
        return jsonify(status), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400