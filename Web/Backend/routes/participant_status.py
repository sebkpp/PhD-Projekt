from threading import Lock

participant_status = {}
participant_slot_map = {}
lock = Lock()

def set_submitted(slot, participant_id=None):
    with lock:
        participant_status[int(slot)] = True
        if participant_id:
            participant_slot_map[int(slot)] = participant_id


def is_submitted(slot):
    with lock:
        return {
            "submitted": participant_status.get(int(slot), False),
            "participant_id": participant_slot_map.get(int(slot))
        }