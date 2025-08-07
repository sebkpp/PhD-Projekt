from Backend.db_session import SessionLocal
from Backend.models.avatar_visibility import AvatarVisibility

def get_all_avatar_visibility():
    session = SessionLocal()
    try:
        entries = session.query(AvatarVisibility).all()
        return [
            {
                "id": entry.avatar_visibility_id,
                "name": entry.avatar_visibility_name,
                "label": entry.label
            } for entry in entries
        ]
    finally:
        session.close()
