from Backend.db_session import Base

# Importiert alle Modelle damit SQLAlchemy sie registriert
from .experiment import Experiment
from .eyetracking import AreaOfInterest, EyeTracking
from .participant import Participant
from .stimulus import StimuliCombination, StimulusType, Stimulus, StimulusCombinationItem, StimulusVisual, \
    StimulusAuditiv, StimulusTactile
from Backend.models.study.study_questionnaire import StudyQuestionnaire
from .study.study_config import StudyConfig
from .study.study_stimuli import StudyStimuli
from Backend.models.trial.trial import Trial
from .handover import Handover
from .questionnaire import Questionnaire, QuestionnaireItem, QuestionnaireResponse
from .avatar_visibility import AvatarVisibility
from .trial.trial_participant_slot import TrialParticipantSlot
from .trial.trial_slot import TrialSlot
from .trial.trial_slot_stimulus import TrialSlotStimulus

__all__ = [
    "Base",
    "Experiment",
    "StimuliCombination",
    "Participant",
    "AreaOfInterest",
    "Trial",
    "Handover",
    "EyeTracking",
    "Questionnaire",
    "QuestionnaireItem",
    "QuestionnaireResponse",
    "StimulusType",
    "Stimulus",
    "StimulusCombinationItem",
    "StimulusVisual",
    "StimulusAuditiv",
    "StimulusTactile",
    "AvatarVisibility",
    "TrialSlotStimulus",
    "TrialSlot",
    "TrialParticipantSlot",
    "StudyQuestionnaire",
    "StudyStimuli",
    "StudyConfig"
]

