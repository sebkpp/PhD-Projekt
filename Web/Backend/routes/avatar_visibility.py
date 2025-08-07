from flask import Blueprint, jsonify
from Backend.services.avatar_visibility_service import get_all_avatar_visibility

avatar_bp = Blueprint('avatar_visibility', __name__)

@avatar_bp.route('/avatar-visibility', methods=['GET'])
def get_avatar_visibility():
    try:
        data = get_all_avatar_visibility()
        return jsonify(data), 200
    except Exception as e:
        print("Fehler beim Laden der Avatar-Visibility:", e)
        return jsonify({"error": "Interner Serverfehler"}), 500