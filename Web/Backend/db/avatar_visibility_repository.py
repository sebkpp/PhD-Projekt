from Backend.models.avatar_visibility import AvatarVisibility

def get_all_avatar_visibility_repo(session):
    return session.query(AvatarVisibility).all()