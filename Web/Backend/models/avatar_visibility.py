from sqlalchemy import Column, Integer, String
from Backend.db_session import Base  # oder wo dein Base definiert ist

class AvatarVisibility(Base):
    __tablename__ = 'avatar_visibility'

    avatar_visibility_id = Column(Integer, primary_key=True, index=True)
    avatar_visibility_name = Column(String, nullable=False)
    label = Column(String, nullable=True)