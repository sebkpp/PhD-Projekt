from Backend.db.stimuli_repository import StimuliRepository

def get_all_stimuli(session):
    s_repo = StimuliRepository(session)

    stimuli = s_repo.get_all_stimuli()
    result = []
    for s in stimuli:
        result.append({
            "id": s.stimulus_id,
            "name": s.name,
            "type": s.stimulus_type.type_name
        })
    return result

