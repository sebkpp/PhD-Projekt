from flask import Blueprint, request, jsonify

from Backend.db.study.study_repository import StudyRepository
from Backend.services.study_service import (
    get_all_studies,
    get_study_by_id,
    create_study,
    update_study,
    delete_study,
    get_experiments_by_study, get_participants_by_study, close_study
)
from Backend.db_session import SessionLocal
from functools import wraps
import logging
logging.basicConfig(level=logging.ERROR)
study_bp = Blueprint('studies', __name__)

def with_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = SessionLocal()
        try:
            return func(session, *args, **kwargs)
        except Exception as e:
            logging.error(e)
            return jsonify({'error': str(e)}), 500
        finally:
            session.close()
    return wrapper

@study_bp.route('/studies', methods=['GET'])
@with_session
def list_studies(session):
    studies = get_all_studies(session)
    return jsonify([s.to_dict() for s in studies]), 200

@study_bp.route('/studies/<int:study_id>', methods=['GET'])
@with_session
def get_study(session, study_id):
    print("Retrieving study with ID:", study_id)
    study = get_study_by_id(session, study_id)
    if not study:
        return jsonify({'error': 'Study not found'}), 404

    #print(f"Retrieved study: {study.to_dict()}")
    return jsonify(study.to_dict()), 200

@study_bp.route('/studies', methods=['POST'])
@with_session
def create_study_route(session):
    data = request.get_json()
    study = create_study(session, data)
    session.commit()
    return jsonify(study.to_dict()), 201

@study_bp.route('/studies/<int:study_id>', methods=['PUT'])
@with_session
def update_study_route(session, study_id):
    data = request.get_json()
    updated = update_study(session, study_id, data)
    if not updated:
        return jsonify({'error': 'Study not found'}), 404
    session.commit()
    return jsonify(updated.to_dict()), 200

@study_bp.route('/studies/<int:study_id>', methods=['DELETE'])
@with_session
def delete_study_route(session, study_id):
    deleted = delete_study(session, study_id)
    if not deleted:
        return jsonify({'error': 'Study not found'}), 404
    session.commit()
    return '', 204

@study_bp.route("/studies/<int:study_id>/experiments", methods=["GET"])
@with_session
def api_get_experiments_by_study(session, study_id):
    print("Fetch experiment by Study for study")
    experiments = get_experiments_by_study(session, study_id)

    print("Result of experiments:", experiments)
    return jsonify(experiments)


@study_bp.route("/studies/<int:study_id>/participants", methods=["GET"])
@with_session
def api_get_participants_by_study(session, study_id):
    participants = get_participants_by_study(session, study_id)
    return jsonify([p.to_dict() for p in participants]), 200


@study_bp.route('/studies/<int:study_id>/close', methods=['POST'])
@with_session
def close_study_route(session, study_id):
    print("Closing study with ID:", study_id)
    study = close_study(session, study_id)
    session.commit()
    if not study:
        return jsonify({'error': 'Study not found or already finished'}), 400
    return jsonify(study.to_dict()), 200