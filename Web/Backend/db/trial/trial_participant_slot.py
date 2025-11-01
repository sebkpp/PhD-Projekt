from Backend.models.trial.trial_participant_slot import TrialParticipantSlot

class TrialParticipantSlotRepository:
    def __init__(self, session):
        self.session = session

    def create(self, trial_slot_id, participant_id):
        participant_slot = TrialParticipantSlot(
            trial_slot_id=trial_slot_id,
            participant_id=participant_id
        )
        self.session.add(participant_slot)
        self.session.commit()
        return participant_slot

    def add(self, participant_slot):
        self.session.add(participant_slot)
        self.session.commit()
        return participant_slot

    def get_by_id(self, participant_slot_id):
        return self.session.query(TrialParticipantSlot).filter_by(participant_slot_id=participant_slot_id).first()

    def get_by_slot_id(self, trial_slot_id):
        return self.session.query(TrialParticipantSlot).filter_by(trial_slot_id=trial_slot_id).all()

    def get_all(self):
        return self.session.query(TrialParticipantSlot).all()

    def delete(self, participant_slot_id):
        slot = self.get_by_id(participant_slot_id)
        if slot:
            self.session.delete(slot)
            self.session.commit()