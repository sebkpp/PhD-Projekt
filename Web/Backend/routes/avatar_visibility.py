from flask import Blueprint, jsonify
from db_conn import get_db

avatar_bp = Blueprint('avatar_visibility', __name__)

@avatar_bp.route('/api/avatar-visibility', methods=['GET'])
def get_avatar_visibility():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT avatar_visibility_id, avatar_visibility_name, label FROM avatar_visibility")
    rows = cur.fetchall()

    return jsonify([
        {"id": row["avatar_visibility_id"], "name": row["avatar_visibility_name"], "label": row["label"]}
        for row in rows
    ])
