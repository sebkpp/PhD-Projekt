from Backend.db.avatar_visibility_repository import get_all_avatar_visibility_repo

def get_all_avatar_visibility(session):
    entries = get_all_avatar_visibility_repo(session)
    return [
        {
            "id": entry.avatar_visibility_id,
            "name": entry.avatar_visibility_name,
            "label": entry.label
        } for entry in entries
    ]
