from flask import Blueprint, request, jsonify
from Backend.db_session import SessionLocal
from Backend.services.questionnaire_response_service import load_questionnaire_responses, save_questionnaire_responses, \
    are_all_questionnaires_in_trial_done, are_all_questionnaires_done, get_questionnaire_responses_for_experiment
from Backend.services.questionnaire_service import get_all_questionnaires, create_questionnaire_with_items, \
    get_questionnaires_for_experiment, get_questionnaires_by_study_id

questionnaire_bp = Blueprint('questionnaire', __name__)

@questionnaire_bp.route('/submit-questionnaire', methods=['POST'])
def submit_questionnaire():
    data = request.get_json()
    print("Received data for questionnaire submission:", data)

    participant_id = data.get('participant_id')
    trial_id = data.get('trial_id')
    questionnaire_name = data.get('questionnaire_name')
    responses = data.get('responses')  # Erwartet dict { item_name: value }

    if not participant_id or not trial_id or not questionnaire_name or not responses:
        return jsonify({"error": "Ungültige Anfrage: fehlende Felder"}), 400

    session = SessionLocal()
    try:
        result = save_questionnaire_responses(
            session,
            participant_id=int(participant_id),
            trial_id=int(trial_id),
            questionnaire_name=questionnaire_name,
            responses=responses
        )
        return jsonify(result)
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@questionnaire_bp.route('/questionnaire-responses', methods=['GET'])
def get_questionnaire_responses():
    participant_id = request.args.get('participant_id', type=int)
    trial_id = request.args.get('trial_id', type=int)
    questionnaire_name = request.args.get('questionnaire_name', type=str)

    if not participant_id or not trial_id or not questionnaire_name:
        return jsonify({"error": "Fehlende Parameter"}), 400

    session = SessionLocal()
    try:
        data = load_questionnaire_responses(session, participant_id, trial_id, questionnaire_name)
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

@questionnaire_bp.route('/questionnaire', methods=['POST'])
def create_questionnaire():
    data = request.get_json()
    name = data.get('name')
    items = data.get('items')  # z.B. ["mental", "physical", "effort"]

    if not name or not items:
        return jsonify({"error": "Name und Items sind erforderlich"}), 400

    session = SessionLocal()
    try:
        questionnaire = create_questionnaire_with_items(session, name, items)
        session.commit()
        return jsonify({
            "status": "ok",
            "questionnaire_id": questionnaire.questionnaire_id,
            "name": questionnaire.name,
            "items": [item.item_name for item in questionnaire.items]
        })
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@questionnaire_bp.route('/questionnaires', methods=['GET'])
def get_questionnaires():
    session = SessionLocal()
    try:
        questionnaires = get_all_questionnaires(session)
        return jsonify({
            "status": "ok",
            "data": questionnaires
        }), 200
    except Exception as e:
        print("Fehler in /api/questionnaires:", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        session.close()

@questionnaire_bp.route('/questionnaires/done', methods=['GET'])
def check_questionnaires_done():
    participant_id = request.args.get('participant', type=int)
    experiment_id = request.args.get('experiment', type=int)

    if not participant_id or not experiment_id:
        return jsonify({"error": "Fehlende Parameter: participant und trial sind erforderlich"}), 400

    session = SessionLocal()
    try:
        all_done = are_all_questionnaires_done(session, participant_id, experiment_id)
        return jsonify({"allDone": all_done}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@questionnaire_bp.route('/questionnaires/trial_done', methods=['GET'])
def check_questionnaires_trial_done():
    participant_id = request.args.get('participant', type=int)
    trial_id = request.args.get('trial', type=int)

    if not participant_id or not trial_id:
        return jsonify({"error": "Fehlende Parameter: participant und trial sind erforderlich"}), 400

    session = SessionLocal()
    try:
        all_done = are_all_questionnaires_in_trial_done(session, participant_id, trial_id)
        return jsonify({"allDone": all_done}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@questionnaire_bp.route('/experiments/<int:experiment_id>/participants/<int:participant_id>/questionnaires', methods=['GET'])
def get_questionnaires_for_experiment_route(experiment_id, participant_id):
    session = SessionLocal()
    try:
        questionnaires = get_questionnaires_for_experiment(session, experiment_id)
        response = {
            "questionnaires": [q.to_dict() for q in questionnaires]
        }

        print("Questionnaires for experiment:", response)
        return jsonify(response), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()


@questionnaire_bp.route('/experiments/<int:experiment_id>/questionnaire-responses', methods=['GET'])
def get_questionnaire_responses_for_experiment_route(experiment_id):
    session = SessionLocal()
    try:
        responses = get_questionnaire_responses_for_experiment(session, experiment_id)
        return jsonify({"status": "ok", "data": responses}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

@questionnaire_bp.route('/questionnaires/study/<int:study_id>', methods=['GET'])
def get_questionnaires_for_study_route(study_id):
    print("Fetching questionnaires for study:", study_id)
    session = SessionLocal()
    try:
        questionnaires = get_questionnaires_by_study_id(session, study_id)

        print("Questionnaires for Study:", questionnaires)
        return jsonify(questionnaires), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

    finally:
        session.close()