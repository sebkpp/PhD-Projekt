from .analysis import analysis_bp
from .experiment import experiment_bp
from .participant import participant_bp
from .questionnaire import questionnaire_bp
from .stimuli import stimuli_bp
from .avatar_visibility import avatar_bp
from .study import study_bp
from .trials import trial_bp
from .handover_routes import handover_bp


def register_routes(app):
    app.register_blueprint(study_bp, url_prefix='/api')
    app.register_blueprint(experiment_bp, url_prefix='/api/experiments')
    app.register_blueprint(participant_bp, url_prefix='/api/participants')
    app.register_blueprint(questionnaire_bp, url_prefix='/api')
    app.register_blueprint(stimuli_bp, url_prefix='/api')
    app.register_blueprint(avatar_bp, url_prefix='/api')
    app.register_blueprint(trial_bp, url_prefix='/api')
    app.register_blueprint(handover_bp, url_prefix='/api')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
