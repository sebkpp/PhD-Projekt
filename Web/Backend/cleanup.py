import threading, time
from datetime import datetime
from routes.participant import connected_participants, lock
from config import TIMEOUT_SECONDS

def cleanup_loop():
    while True:
        now = datetime.utcnow()
        with lock:
            expired = [pid for pid, ts in connected_participants.items()
                       if (now - ts).total_seconds() > TIMEOUT_SECONDS]
            for pid in expired:
                print(f"Spieler inaktiv entfernt: {pid}")
                del connected_participants[pid]
        time.sleep(5)

def start_cleanup_thread():
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
