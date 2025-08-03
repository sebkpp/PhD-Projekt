from .experiment import experiment_bp
from .participant import participant_bp
from .questionnaire import questionnaire_bp
from .stimuli import stimuli_bp
from .avatar_visibility import avatar_bp
from .trials import trials_bp


def register_routes(app):
    app.register_blueprint(experiment_bp, url_prefix='/api')
    app.register_blueprint(participant_bp, url_prefix='/api')
    app.register_blueprint(questionnaire_bp, url_prefix='/api')
    app.register_blueprint(stimuli_bp)
    app.register_blueprint(avatar_bp)
    app.register_blueprint(trials_bp, url_prefix='/api')
