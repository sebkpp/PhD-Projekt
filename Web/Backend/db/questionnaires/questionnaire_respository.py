from Backend.models import Experiment, Trial, StudyQuestionnaire
from Backend.models.questionnaire import Questionnaire, QuestionnaireItem

class QuestionnaireRepository:
    def __init__(self, session):
        self.session = session

    def get_questionnaire_by_name(self, name: str):
        return self.session.query(Questionnaire).filter_by(name=name).first()

    def create_questionnaire(self, name: str):
        questionnaire = Questionnaire(name=name)
        self.session.add(questionnaire)
        self.session.flush()
        self.session.refresh(questionnaire)
        return questionnaire

    def add_questionnaire_item(self, questionnaire_id: int, item_name: str):
        item = QuestionnaireItem(
            questionnaire_id=questionnaire_id,
            item_name=item_name
        )
        self.session.add(item)
        self.session.flush()
        self.session.refresh(item)
        return item

    def get_questionnaire_items(self, questionnaire_id: int):
        return self.session.query(QuestionnaireItem).filter_by(questionnaire_id=questionnaire_id).all()

    def get_all_questionnaires(self):
        return self.session.query(Questionnaire).all()

    def get_questionnaires_by_list_of_ids(self, questionnaire_ids: list[int]):
        return self.session.query(Questionnaire).filter(Questionnaire.questionnaire_id.in_(questionnaire_ids)).all()

    def get_by_study_id(self, study_id: int):
        study_questionnaires = self.session.query(StudyQuestionnaire).filter_by(study_id=study_id).all()
        questionnaire_ids = list(set(sq.questionnaire_id for sq in study_questionnaires))
        return self.get_questionnaires_by_list_of_ids(questionnaire_ids)

    def get_by_experiment_id(self, experiment_id: int):
        experiment = self.session.query(Experiment).get(experiment_id)
        if not experiment or not hasattr(experiment, "study_id"):
            return []
        return self.get_by_study_id(experiment.study_id)

    def get_by_trial_id(self, trial_id: int):
        trial = self.session.query(Trial).filter_by(trial_id=trial_id).first()
        if not trial or not hasattr(trial, "experiment_id"):
            return []
        experiment = self.session.query(Experiment).get(trial.experiment_id)
        questionnaires = self.get_by_experiment_id(experiment.experiment_id)
        return questionnaires
