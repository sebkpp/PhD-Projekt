from Backend.models.trial.trial_slot import TrialSlot

class TrialSlotRepository:
    def __init__(self, session):
        self.session = session

    def create(self, trial_id: int, slot_number: int) -> TrialSlot:
        trial_slot = TrialSlot(
            trial_id=trial_id,
            slot=slot_number,
            avatar_visibility_id=1,
        )
        self.session.add(trial_slot)
        self.session.flush()
        self.session.refresh(trial_slot)
        return trial_slot

    def add(self, trial_slot):
        self.session.add(trial_slot)
        self.session.commit()
        return trial_slot

    def get_by_id(self, trial_slot_id):
        return self.session.query(TrialSlot).filter_by(trial_slot_id=trial_slot_id).first()

    def get_by_trial_id(self, trial_id: int, slot: int = None):
        query = self.session.query(TrialSlot).filter_by(trial_id=trial_id)
        if slot is not None:
            query = query.filter_by(slot=slot)
        return query.all()

    def get_all(self):
        return self.session.query(TrialSlot).all()

    def delete(self, trial_slot_id):
        slot = self.get_by_id(trial_slot_id)
        if slot:
            self.session.delete(slot)
            self.session.commit()