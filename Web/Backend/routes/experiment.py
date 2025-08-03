from flask import Blueprint, request, jsonify
from db_conn import get_db

experiment_bp = Blueprint('experiment', __name__)

@experiment_bp.route('/experiments', methods=['POST'])
def create_experiment():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    researcher = data.get('researcher')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO experiment (name, description, researcher)
        VALUES (%s, %s, %s)
        RETURNING experiment_id;
    """, (name, description, researcher))
    experiment_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({ "experimentId": experiment_id }), 201
