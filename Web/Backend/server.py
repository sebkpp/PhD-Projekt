from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)
connected_players = {}  # Format: {player_id: last_seen_utc}
lock = threading.Lock()

TIMEOUT_SECONDS = 10

@app.route("/join", methods=["POST"])
def player_join():
    data = request.get_json()
    player_id = data.get("player_id")
    if not player_id:
        return jsonify({"status": "error", "message": "Missing player_id"}), 400

    now = datetime.utcnow()
    with lock:
        connected_players[player_id] = now

    print(f"✅ Spieler verbunden: {player_id}")
    return jsonify({"status": "joined", "player_id": player_id})

@app.route("/heartbeat", methods=["POST"])
def player_heartbeat():
    data = request.get_json()
    player_id = data.get("player_id")
    if not player_id:
        return jsonify({"status": "error", "message": "Missing player_id"}), 400

    now = datetime.utcnow()
    with lock:
        connected_players[player_id] = now

    return jsonify({"status": "heartbeat", "player_id": player_id})

@app.route("/players", methods=["GET"])
def list_players():
    with lock:
        return jsonify({
            pid: ts.isoformat() for pid, ts in connected_players.items()
        })

@app.route("/", methods=["GET"])
def serve_webpage():
    return send_from_directory('.', 'players.html')

def cleanup_loop():
    while True:
        now = datetime.utcnow()
        with lock:
            to_remove = [pid for pid, ts in connected_players.items()
                         if (now - ts).total_seconds() > TIMEOUT_SECONDS]
            for pid in to_remove:
                print(f"⏱️ Spieler inaktiv entfernt: {pid}")
                del connected_players[pid]
        time.sleep(5)

if __name__ == '__main__':
    # Cleanup-Thread starten
    threading.Thread(target=cleanup_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)