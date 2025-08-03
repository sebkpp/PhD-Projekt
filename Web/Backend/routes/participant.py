from flask import Blueprint, request, jsonify
from datetime import datetime
from .participant_status import set_submitted, is_submitted
from db_conn import get_db
import threading

participant_bp = Blueprint('participant', __name__)

# Globale Spieler-Datenstruktur (Shared State)
connected_participants = {}  # Format: {participant_id: last_seen_utc}
lock = threading.Lock()

TIMEOUT_SECONDS = 10

@participant_bp.route("/join", methods=["POST"])
def player_join():
    data = request.get_json()
    player_id = data.get("player_id")
    if not player_id:
        return jsonify({"status": "error", "message": "Missing player_id"}), 400

    now = datetime.utcnow()
    with lock:
        connected_participants[player_id] = now

    print(f"✅ Spieler verbunden: {player_id}")
    return jsonify({"status": "joined", "player_id": player_id})


@participant_bp.route("/heartbeat", methods=["POST"])
def player_heartbeat():
    data = request.get_json()
    player_id = data.get("player_id")
    if not player_id:
        return jsonify({"status": "error", "message": "Missing player_id"}), 400

    now = datetime.utcnow()
    with lock:
        connected_participants[player_id] = now

    return jsonify({"status": "heartbeat", "player_id": player_id})


@participant_bp.route("/participants", methods=["GET"])
def list_players():
    with lock:
        return jsonify({
            pid: ts.isoformat() for pid, ts in connected_participants.items()
        })

@participant_bp.route('/participants', methods=['POST'])
def register_participant():
    data = request.get_json()

    age = data.get("age")
    gender = data.get("gender")
    handedness = data.get("handedness")

    if not age or not gender or not handedness:
        return jsonify({"error": "Unvollständige Daten"}), 400

    conn = get_db()
    cur = conn.cursor()

    # Teilnehmer anlegen
    cur.execute("""
        INSERT INTO participant (age, gender, handedness)
        VALUES (%s, %s, %s)
        RETURNING participant_id
    """, (age, gender, handedness))

    participant_id = cur.fetchone()["participant_id"]

    conn.commit()
    conn.close()

    return jsonify({"participant_id": participant_id}), 201

@participant_bp.route('/participants/submit', methods=['POST'])
def set_submit_status():
    data = request.get_json()
    slot = data.get('slot')
    participant_id = data.get('participant_id')
    if slot is None:
        return jsonify({"error": "Missing slot"}), 400

    set_submitted(slot, participant_id)
    return jsonify({"status": "ok"}), 200

@participant_bp.route('/participants/status/<int:slot>', methods=['GET'])
def get_submit_status(slot):
    status = is_submitted(slot)
    return jsonify(status), 200
