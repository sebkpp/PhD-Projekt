from Backend.models.trial import Trial, TrialParticipantItem
from Backend.models.stimulus import StimulusCombinationItem, Stimulus, StimulusType
from Backend.services.stimuli_service import get_stimulus_type_map, ensure_stimulus_combination


def save_trials(session, experiment_id, trials):
    stimulus_type_map = get_stimulus_type_map(session)

    for trial_data in trials:
        trial_number = trial_data["trial_number"]
        trial = Trial(experiment_id=experiment_id, trial_number=trial_number)
        session.add(trial)
        session.flush()

        for _, config in trial_data["participants"].items():
            avatar_id = config["avatar"]
            participant_id = config["participant_id"]
            selected_stimuli_ids = list(config.get("selectedStimuli", {}).values())

            stimulus_combination = None
            if selected_stimuli_ids:
                stimulus_combination = ensure_stimulus_combination(session, selected_stimuli_ids, stimulus_type_map)

            session.add(TrialParticipantItem(
                trial_id=trial.trial_id,
                participant_id=int(participant_id),
                avatar_visibility_id=avatar_id,
                stimulus_combination_id=stimulus_combination.stimulus_combination_id if stimulus_combination else None
            ))

    return {
        "status": "ok",
        "message": f"{len(trials)} Trials erfolgreich gespeichert."
    }


def get_trials_for_experiment(session, experiment_id):
    # Hole alle relevanten Trial-Informationen samt Stimuli
    rows = session.query(
        Trial.trial_id,
        Trial.trial_number,
        TrialParticipantItem.participant_id,
        TrialParticipantItem.avatar_visibility_id,
        Stimulus.stimulus_id,
        StimulusType.type_name
    ).join(TrialParticipantItem, Trial.trial_id == TrialParticipantItem.trial_id
           ).outerjoin(StimulusCombinationItem,
                       TrialParticipantItem.stimulus_combination_id == StimulusCombinationItem.stimulus_combination_id
                       ).outerjoin(Stimulus,
                                   StimulusCombinationItem.stimulus_id == Stimulus.stimulus_id
                                   ).outerjoin(StimulusType,
                                               Stimulus.stimulus_type_id == StimulusType.stimulus_type_id
                                               ).filter(
        Trial.experiment_id == experiment_id
    ).order_by(Trial.trial_number, TrialParticipantItem.participant_id).all()

    # Transformieren
    trial_map = {}

    for row in rows:
        trial_id = row.trial_id
        trial_number = row.trial_number
        participant_id = row.participant_id
        avatar = row.avatar_visibility_id
        stimulus_id = row.stimulus_id
        type_name = row.type_name

        if trial_id not in trial_map:
            trial_map[trial_id] = {
                "trial_id": trial_id,
                "trial_number": trial_number,
                "participants": {}
            }

        if participant_id not in trial_map[trial_id]["participants"]:
            trial_map[trial_id]["participants"][participant_id] = {
                "participant_id": participant_id,
                "avatar": avatar,
                "selectedStimuli": {}
            }

        if type_name and stimulus_id:
            type_code = type_name.lower()[:3]  # z. B. visual → vis
            trial_map[trial_id]["participants"][participant_id]["selectedStimuli"][type_code] = stimulus_id

    return list(trial_map.values())
