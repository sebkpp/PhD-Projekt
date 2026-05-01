from Backend.db.experiment.experiment_repository import ExperimentRepository
from Backend.db.questionnaires.questionnaire_respository import QuestionnaireRepository
from Backend.db.study.study_questionnaire_repository import StudyQuestionnaireRepository


def create_questionnaire(session, name, scale_type: str = 'slider', scale_min: float = 0, scale_max: float = 100):
    q_repo = QuestionnaireRepository(session)

    existing = q_repo.get_questionnaire_by_name(name)
    if existing:
        return existing

    return q_repo.create_questionnaire(name, scale_type=scale_type, scale_min=scale_min, scale_max=scale_max)

def add_questionnaire_item(session, questionnaire_id, item_name, item_label=None, item_description=None, min_label=None, max_label=None, order_index=0):
    q_repo = QuestionnaireRepository(session)
    return q_repo.add_questionnaire_item(
        questionnaire_id, item_name,
        item_label=item_label, item_description=item_description,
        min_label=min_label, max_label=max_label, order_index=order_index,
    )


def get_questionnaire_by_name(session, name):
    q_repo = QuestionnaireRepository(session)
    return q_repo.get_questionnaire_by_name(name)

def get_questionnaire_items(session, questionnaire_id):
    q_repo = QuestionnaireRepository(session)
    return q_repo.get_questionnaire_items(questionnaire_id)

def create_questionnaire_with_items(session, name, items: list, scale_type: str = 'slider', scale_min: float = 0, scale_max: float = 100):
    """items kann eine Liste von Strings (Rückwärtskompatibilität) oder Dicts mit Item-Metadaten sein."""
    questionnaire = create_questionnaire(session, name, scale_type=scale_type, scale_min=scale_min, scale_max=scale_max)
    for idx, item in enumerate(items):
        if isinstance(item, str):
            add_questionnaire_item(session, questionnaire.questionnaire_id, item, order_index=idx)
        else:
            add_questionnaire_item(
                session,
                questionnaire.questionnaire_id,
                item_name=item.get('item_name', ''),
                item_label=item.get('item_label'),
                item_description=item.get('item_description'),
                min_label=item.get('min_label'),
                max_label=item.get('max_label'),
                order_index=item.get('order_index', idx),
            )
    return questionnaire

def get_questionnaire_by_id(session, questionnaire_id: int):
    q_repo = QuestionnaireRepository(session)
    return q_repo.get_by_id(questionnaire_id)

def get_all_questionnaires(session):
    q_repo = QuestionnaireRepository(session)
    questionnaires = q_repo.get_all_questionnaires()
    return [q.to_dict() for q in questionnaires]

def get_questionnaires_for_experiment(session, experiment_id):
    e_repo = ExperimentRepository(session)
    experiment = e_repo.get_by_id(experiment_id)
    return experiment.questionnaires if experiment else []

def get_questionnaires_by_study_id(session, study_id):
    sq_repo = StudyQuestionnaireRepository(session)
    return sq_repo.get_by_study_id(study_id)

def get_questionnaires_by_trial_id(session, trial_id):
    q_repo = QuestionnaireRepository(session)
    return q_repo.get_by_trial_id(trial_id)