from flask import Blueprint, request, jsonify
from Backend.db_conn import get_db

questionnaire_bp = Blueprint('questionnaire', __name__)

@questionnaire_bp.route('/submit-nasatlx', methods=['POST'])
def submit_nasatlx():
    data = request.get_json()

    participant_id = data.get('userId')
    trial_id = data.get('trialId')
    responses = data.get('responses')

    if not participant_id or not trial_id or not responses:
        return jsonify({ "status": "error", "message": "Ungültige Anfrage" }), 400

    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO nasatlx_responses (
                participant_id,
                trial_id,
                mental,
                physical,
                temporal,
                performance,
                effort,
                frustration
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            participant_id,
            trial_id,
            responses.get("mental"),
            responses.get("physical"),
            responses.get("temporal"),
            responses.get("performance"),
            responses.get("effort"),
            responses.get("frustration")
        ))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({ "status": "success" }), 200

    except Exception as e:
        print(f"❌ Fehler beim Speichern des Fragebogens: {e}")
        return jsonify({ "status": "error", "message": str(e) }), 500

@questionnaire_bp.route('/active-questionnaire', methods=['GET'])
def get_active_questionnaire():
    user = request.args.get('user')
    if not user:
        return jsonify({"error": "Missing user"}), 400

    conn = get_db()
    cur = conn.cursor()

    # Beispielhafte Abfrage - passe sie an dein Schema an!
    # Hier wird angenommen, dass du eine Tabelle 'trials' hast, mit participant_id und einem Status-Feld.
    cur.execute("""
        SELECT trial_id, type
        FROM trial
        WHERE participant_id = %s AND status = 'active'
        LIMIT 1
    """, (user,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        trial_id, q_type = row
        return jsonify({"type": q_type, "trialId": trial_id})
    else:
        return jsonify({"type": "waiting"})  # Kein aktiver Fragebogen gefunden
