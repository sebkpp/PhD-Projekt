from Backend.models.stimulus import Stimulus, StimulusType, StimuliCombination, StimulusCombinationItem
from sqlalchemy.exc import IntegrityError

def get_all_stimuli(session):
    stimuli = session.query(Stimulus).join(Stimulus.stimulus_type).all()
    result = []
    for s in stimuli:
        result.append({
            "id": s.stimulus_id,
            "name": s.name,
            "type": s.stimulus_type.type_name
        })
    return result

def get_stimulus_type_map(session):
    stimuli = session.query(Stimulus).join(StimulusType).all()
    type_name_to_code = {
        'visual': 'VIS',
        'auditory': 'AUD',
        'tactile': 'TAK'
    }
    stimulus_type_map = {
        stim.stimulus_id: type_name_to_code.get(stim.stimulus_type.type_name.lower())
        for stim in stimuli
    }
    return stimulus_type_map

def ensure_stimulus_combination(session, selected_stimuli_ids, stimulus_type_map):
    type_abbrs = []
    for sid in selected_stimuli_ids:
        type_code = stimulus_type_map.get(int(sid))
        if not type_code:
            raise ValueError(f"Kein Stimulus-Typ für stimulus_id={sid} gefunden.")
        type_abbrs.append(type_code)

    readable_combination = ','.join(sorted(type_abbrs))

    stimulus_combination = session.query(StimuliCombination).filter_by(combination=readable_combination).one_or_none()
    if not stimulus_combination:
        stimulus_combination = StimuliCombination(combination=readable_combination)
        session.add(stimulus_combination)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            stimulus_combination = session.query(StimuliCombination).filter_by(combination=readable_combination).one()

        for stimulus_id in selected_stimuli_ids:
            exists = session.query(StimulusCombinationItem).filter_by(
                stimulus_combination_id=stimulus_combination.stimulus_combination_id,
                stimulus_id=stimulus_id
            ).first()
            if not exists:
                session.add(StimulusCombinationItem(
                    stimulus_combination_id=stimulus_combination.stimulus_combination_id,
                    stimulus_id=stimulus_id
                ))
        session.flush()

    return stimulus_combination
