from threading import Lock

# Temporärer In-Memory-Speicher
_experiment_submission_state = {}
_lock = Lock()

def submit_participant_to_slot(experiment_id, slot, participant_id=None):
    """
    Markiert den Slot eines Experiments als 'submitted' mit optionaler participant_id.
    """
    with _lock:
        exp_id = int(experiment_id)
        slot = int(slot)

        if exp_id not in _experiment_submission_state:
            _experiment_submission_state[exp_id] = {}

        _experiment_submission_state[exp_id][slot] = {
            "submitted": True,
            "participant_id": participant_id
        }


def get_submission_status(experiment_id, slot):
    """
    Gibt zurück, ob der Slot eines Experiments bereits als 'submitted' markiert wurde.
    """
    with _lock:
        exp_id = int(experiment_id)
        slot = int(slot)

        return _experiment_submission_state.get(exp_id, {}).get(slot, {
            "submitted": False,
            "participant_id": None
        })
