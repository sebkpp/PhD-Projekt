from Backend.models import TrialSlot, TrialSlotStimulus
from Backend.models.stimulus import Stimulus

class StimuliRepository:
    def __init__(self, session):
        self.session = session

    def get_all_stimuli(self):
        return self.session.query(Stimulus).join(Stimulus.stimulus_type).all()

    def get_stimuli_for_trial(self, trial_id):
        slots = self.session.query(TrialSlot).filter_by(trial_id=trial_id).all()
        slot_ids = [slot.trial_slot_id for slot in slots]

        tss = self.session.query(TrialSlotStimulus).filter(TrialSlotStimulus.trial_slot_id.in_(slot_ids)).all()
        stimulus_ids = [t.stimulus_id for t in tss]
        stimuli = self.session.query(Stimulus).filter(Stimulus.stimulus_id.in_(stimulus_ids)).all()
        return stimuli

    def get_stimuli_for_trials(self, trial_ids):
        slots = self.session.query(TrialSlot).filter(TrialSlot.trial_id.in_(trial_ids)).all()
        slot_map = {}
        for slot in slots:
            slot_map.setdefault(slot.trial_id, []).append(slot.trial_slot_id)
        all_slot_ids = [sid for sids in slot_map.values() for sid in sids]
        tss = self.session.query(TrialSlotStimulus).filter(
            TrialSlotStimulus.trial_slot_id.in_(all_slot_ids)
        ).all()
        stimulus_ids = set(t.stimulus_id for t in tss)
        stimuli = self.session.query(Stimulus).filter(Stimulus.stimulus_id.in_(stimulus_ids)).all()
        stimulus_dict = {stimulus.stimulus_id: stimulus.to_dict() for stimulus in stimuli}

        trial_stimuli = {trial_id: [] for trial_id in trial_ids}
        trial_stimulus_ids = {trial_id: set() for trial_id in trial_ids}
        for t in tss:
            for trial_id, slot_ids in slot_map.items():
                if t.trial_slot_id in slot_ids and t.stimulus_id not in trial_stimulus_ids[trial_id]:
                    trial_stimuli[trial_id].append(stimulus_dict[t.stimulus_id])
                    trial_stimulus_ids[trial_id].add(t.stimulus_id)
        return {trial_id: trial_stimuli[trial_id] for trial_id in trial_stimuli}

    def get_stimulus_type_by_id(self, stimulus_id):
        stimulus = self.session.query(Stimulus).filter_by(stimulus_id=stimulus_id).join(Stimulus.stimulus_type).first()
        if stimulus and stimulus.stimulus_type:
            return stimulus.stimulus_type.type_name
        return None

