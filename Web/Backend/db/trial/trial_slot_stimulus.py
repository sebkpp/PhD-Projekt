from Backend.models.trial.trial_slot_stimulus import TrialSlotStimulus

class TrialSlotStimulusRepository:
    def __init__(self, session):
        self.session = session

    def create(self, trial_slot_id: int, stimulus_id: int) -> TrialSlotStimulus:
        trial_slot_stimulus = TrialSlotStimulus(
            trial_slot_id=trial_slot_id,
            stimulus_id=stimulus_id
        )
        self.session.add(trial_slot_stimulus)
        self.session.flush()
        self.session.refresh(trial_slot_stimulus)
        return trial_slot_stimulus

    def add(self, trial_slot_stimulus):
        self.session.add(trial_slot_stimulus)
        self.session.commit()
        return trial_slot_stimulus

    def get_by_id(self, stimulus_id):
        return self.session.query(TrialSlotStimulus).filter_by(stimulus_id=stimulus_id).first()

    def get_all(self):
        return self.session.query(TrialSlotStimulus).all()

    def delete(self, stimulus_id):
        stimulus = self.get_by_id(stimulus_id)
        if stimulus:
            self.session.delete(stimulus)
            self.session.commit()