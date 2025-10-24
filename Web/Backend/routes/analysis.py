from flask import Blueprint, jsonify, request

from Backend.db_session import SessionLocal
from Backend.services.data_analysis.performance_analysis_service import analyze_experiment_performance
from Backend.services.data_analysis.questionnaire_analysis_service import analyze_experiment_questionnaires

analysis_bp = Blueprint("analysis", __name__, url_prefix="/api/analysis")

@analysis_bp.route("/questionnaires", methods=["GET"])
def questionnaire_analysis():
    return jsonify(None)

@analysis_bp.route("/study/<int:study_id>/questionnaires", methods=["GET"])
def study_questionnaires_analysis(study_id):
    return jsonify(None)

@analysis_bp.route("/experiment/<int:experiment_id>/questionnaires", methods=["GET"])
def experiment_questionnaire_analysis(experiment_id):
    session = SessionLocal()
    try:
        result = analyze_experiment_questionnaires(session, experiment_id)
        if not result:
            return jsonify({"error": "No Result"}), 404
        return jsonify(result), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@analysis_bp.route("/performance", methods=["GET"])
def all_performance_analysis():
    return jsonify(None)

@analysis_bp.route("/study/<int:study_id>/performance", methods=["GET"])
def study_performance_analysis(study_id):
    return jsonify(None)

@analysis_bp.route("/experiment/<int:experiment_id>/performance", methods=["GET"])
def experiment_performance_analysis(experiment_id):
    session = SessionLocal()
    try:
        result = analyze_experiment_performance(session, experiment_id)
        if not result:
            return jsonify({"error": "No Result"}), 404
        return jsonify(result), 201
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@analysis_bp.route("/eyetracking", methods=["GET"])
def all_eyetracking_analysis():
    return jsonify(None)

@analysis_bp.route("/study/<int:study_id>/eyetracking", methods=["GET"])
def study_eyetracking_analysis(study_id):
    return jsonify(None)

@analysis_bp.route("/experiment/<int:experiment_id>/eyetracking", methods=["GET"])
def experiment_eyetracking_analysis(experiment_id):
    return jsonify(None)