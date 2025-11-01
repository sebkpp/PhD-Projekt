from sqlalchemy.orm import Session
from Backend.models.trial.trial import Trial, TrialParticipantStimulus
from Backend.models.stimulus import StimulusType, Stimulus

# def create_trial_participant_item(db: Session, trial_id: int, participant_id: int, avatar_visibility_id: int) -> TrialParticipantItem:
#     item = TrialParticipantItem(
#         trial_id=trial_id,
#         participant_id=participant_id,
#         avatar_visibility_id=avatar_visibility_id
#     )
#     db.add(item)
#     db.flush()
#     db.refresh(item)
#     return item

# def get_trial_details_for_experiment(db: Session, experiment_id: int):
#     return db.query(
#         Trial.trial_id,
#         Trial.trial_number,
#         TrialParticipantItem.participant_id,
#         TrialParticipantItem.avatar_visibility_id,
#         TrialParticipantStimulus.stimulus_id,
#         StimulusType.type_name
#     ).join(
#         TrialParticipantItem, Trial.trial_id == TrialParticipantItem.trial_id
#     ).outerjoin(
#         TrialParticipantStimulus, TrialParticipantItem.trial_participant_item_id == TrialParticipantStimulus.trial_participant_item_id
#     ).outerjoin(
#         Stimulus, TrialParticipantStimulus.stimulus_id == Stimulus.stimulus_id
#     ).outerjoin(
#         StimulusType, Stimulus.stimulus_type_id == StimulusType.stimulus_type_id
#     ).filter(
#         Trial.experiment_id == experiment_id
#     ).order_by(
#         Trial.trial_number
#     ).all()

# def get_participant_item_for_trial(db: Session, trial_id: int, participant_id: int):
#     return db.query(TrialParticipantItem).filter(
#         TrialParticipantItem.trial_id == trial_id,
#         TrialParticipantItem.participant_id == participant_id
#     ).first()

# def get_all_participant_items_for_trial(db: Session, trial_id: int):
#     return db.query(TrialParticipantItem).filter(TrialParticipantItem.trial_id == trial_id).all()
