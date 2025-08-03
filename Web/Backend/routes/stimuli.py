from flask import Blueprint, jsonify
from db_conn import get_db

stimuli_bp = Blueprint('stimuli', __name__)

@stimuli_bp.route('/api/stimuli', methods=['GET'])
def get_stimuli():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.stimulus_id, s.name, st.type_name AS type
        FROM stimuli s
        JOIN stimulus_type st ON s.stimulus_type_id = st.stimulus_type_id
    """)
    rows = cur.fetchall()

    stimuli = [
        {"id": row["stimulus_id"], "name": row["name"], "type": row["type"]}
        for row in rows
    ]
    return jsonify(stimuli)
