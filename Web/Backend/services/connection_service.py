import threading
from datetime import datetime, timedelta

lock = threading.Lock()

mock_connection_status = {"1": False, "2": False}
heartbeat_timestamps = {}

TIMEOUT_SECONDS = 10

def player_joined(player_id: str) -> bool:
    if player_id not in ["1", "2"]:
        return False
    now = datetime.utcnow()
    with lock:
        mock_connection_status[player_id] = True
        heartbeat_timestamps[player_id] = now
    print(f"✅ Spieler verbunden: {player_id}")
    return True

def update_heartbeat(player_id):
    if player_id not in ["1", "2"]:
        return False

    now = datetime.utcnow()
    with lock:
        mock_connection_status[player_id] = True
        heartbeat_timestamps[player_id] = now
    return True

def get_connection_status():
    now = datetime.utcnow()
    timeout = timedelta(seconds=TIMEOUT_SECONDS)
    status = {}

    with lock:
        for pid in ["1", "2"]:
            last = heartbeat_timestamps.get(pid)
            is_connected = last and (now - last) < timeout
            status[pid] = bool(is_connected)

    return status
