import threading, time
from datetime import datetime, timedelta
from Backend.services.connection_service import heartbeat_timestamps, mock_connection_status, TIMEOUT_SECONDS, lock
from Backend.config import TIMEOUT_SECONDS

def cleanup_loop():
    while True:
        now = datetime.utcnow()
        timeout_delta = timedelta(seconds=TIMEOUT_SECONDS)

        expired = []

        with lock:
            # Sammle alle Player-IDs, deren letzter Heartbeat älter als TIMEOUT_SECONDS ist
            for pid, last_seen in list(heartbeat_timestamps.items()):
                if now - last_seen > timeout_delta:
                    expired.append(pid)

            # Entferne diese Einträge aus heartbeat_timestamps und mock_connection_status
            for pid in expired:
                print(f"Spieler inaktiv entfernt: {pid}")
                heartbeat_timestamps.pop(pid, None)
                mock_connection_status[pid] = False

        time.sleep(5)

def start_cleanup_thread():
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
