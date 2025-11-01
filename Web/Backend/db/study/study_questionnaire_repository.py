from Backend.models.study.study_questionnaire import StudyQuestionnaire

class StudyQuestionnaireRepository:
    def __init__(self, session):
        self.session = session

    def create(self, study_id: int, questionnaire_id: int, idx: int):
        new_entry = StudyQuestionnaire(study_id=study_id, questionnaire_id=questionnaire_id, order_index=idx)
        self.session.add(new_entry)
        self.session.commit()
        return new_entry

    def get_by_study_id(self, study_id: int):
        entries = (
            self.session.query(StudyQuestionnaire)
            .filter_by(study_id=study_id)
            .order_by(StudyQuestionnaire.order_index)
            .all()
        )
        return [
            {
                "questionnaire_id": entry.questionnaire_id,
                "order_index": entry.order_index,
                "name": entry.questionnaire.name if entry.questionnaire else None
            }
            for entry in entries
        ]

    def update(self, study_id: int, questionnaire_id: int):
        entry = self.session.query(StudyQuestionnaire).filter_by(study_id=study_id, questionnaire_id=questionnaire_id).first()
        if entry:
            entry.study_id = study_id
            entry.questionnaire_id = questionnaire_id
            self.session.commit()
            self.session.refresh(entry)
        return entry

    def delete(self, study_id: int, questionnaire_id: int):
        entry = self.session.query(StudyQuestionnaire).filter_by(study_id=study_id, questionnaire_id=questionnaire_id).first()
        if entry:
            self.session.delete(entry)
            self.session.commit()

    def delete_all_by_study_id(self, study_id: int):
        self.session.query(StudyQuestionnaire).filter_by(study_id=study_id).delete()
        self.session.commit()