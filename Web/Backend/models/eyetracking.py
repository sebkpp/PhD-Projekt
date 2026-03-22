from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime,
    ForeignKey, UniqueConstraint, Double
)
from sqlalchemy.orm import relationship
from Backend.db_session import Base

class AreaOfInterest(Base):
    __tablename__ = "area_of_interest"

    aoi_id = Column(Integer, primary_key=True)
    aoi = Column(String(255), nullable=False)
    label = Column(String(255), nullable=False)

    eye_trackings = relationship("EyeTracking", back_populates="aoi")

class EyeTracking(Base):
    __tablename__ = "eye_tracking"

    eye_tracking_id = Column(Integer, primary_key=True)
    starttime = Column(DateTime)
    endtime = Column(DateTime)
    duration = Column(Integer)
    participant_id = Column(Integer, ForeignKey("participant.participant_id"), nullable=False)
    handover_id = Column(Integer, ForeignKey("handover.handover_id"), nullable=False)
    aoi_id = Column(Integer, ForeignKey("area_of_interest.aoi_id"), nullable=False)

    participant = relationship("Participant", back_populates="eye_trackings")
    handover = relationship("Handover", back_populates="eye_trackings")
    aoi = relationship("AreaOfInterest", back_populates="eye_trackings")