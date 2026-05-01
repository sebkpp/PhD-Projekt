from Backend.models import Experiment
from Backend.models.questionnaire import Questionnaire, QuestionnaireItem, QuestionnaireResponse

class QuestionnaireResponseRepository:
    def __init__(self, session):
        self.session = session

    def add_questionnaire_response(self, participant_id, trial_id, questionnaire_item_id, response_value):
        response = QuestionnaireResponse(
            participant_id=participant_id,
            trial_id=trial_id,
            questionnaire_item_id=questionnaire_item_id,
            response_value=response_value
        )
        self.session.add(response)

    def get_questionnaire_responses(self, participant_id, trial_id, item_ids):
        return self.session.query(QuestionnaireResponse).filter(
            QuestionnaireResponse.participant_id == participant_id,
            QuestionnaireResponse.trial_id == trial_id,
            QuestionnaireResponse.questionnaire_item_id.in_(item_ids)
        ).all()

    def get_questionnaire_responses_for_trials(self, trial_ids: list[int]):
        return self.session.query(QuestionnaireResponse).filter(
            QuestionnaireResponse.trial_id.in_(trial_ids)
        ).all()