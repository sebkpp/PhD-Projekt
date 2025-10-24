from Backend.models.trial.trial import Trial

class TrialRepository:
    def __init__(self, session):
        self.session = session

    def create(self, experiment_id: int, trial_number: int) -> Trial:
        trial = Trial(
            experiment_id=experiment_id,
            trial_number=trial_number
        )
        self.session.add(trial)
        self.session.flush()
        self.session.refresh(trial)
        return trial

    def add(self, trial):
        self.session.add(trial)
        self.session.commit()
        return trial

    def get_by_id(self, trial_id):
        trial = self.session.query(Trial).filter_by(trial_id=trial_id).first()
        return trial

    def get_all(self):
        return self.session.query(Trial).all()

    def delete(self, trial_id):
        trial = self.get_by_id(trial_id)
        if trial:
            self.session.delete(trial)
            self.session.commit()

    def set_trial_finished(self, trial_id: int):
        trial = self.get_by_id(trial_id)
        if trial:
            trial.is_finished = True
            self.session.commit()
            return trial
        return None

    def get_by_experiment_id(self, experiment_id: int):
        return self.session.query(Trial).filter(Trial.experiment_id == experiment_id).order_by(Trial.trial_number.desc()).all()

    def get_by_study_id(self, study_id):
        return self.session.query(Trial).filter_by(study_id=study_id).all()