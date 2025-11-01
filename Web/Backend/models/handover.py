# models/handover.py
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from Backend.db_session import Base
from sqlalchemy.orm import relationship

class Handover(Base):
    __tablename__ = "handover"

    handover_id = Column(Integer, primary_key=True, index=True)
    grasped_object = Column(String(255))
    giver_grasped_object = Column(TIMESTAMP)  # Zeitstempel
    receiver_touched_object = Column(TIMESTAMP)
    receiver_grasped_object = Column(TIMESTAMP)
    giver_released_object = Column(TIMESTAMP)
    trial_id = Column(Integer, ForeignKey("trial.trial_id"), nullable=False)
    giver = Column(Integer, ForeignKey("participant.participant_id"), nullable=False)
    receiver = Column(Integer, ForeignKey("participant.participant_id"))

    trial = relationship("Trial", back_populates="handovers")
    giver_participant = relationship("Participant", foreign_keys=[giver], back_populates="handovers_given")
    receiver_participant = relationship("Participant", foreign_keys=[receiver], back_populates="handovers_received")
    eye_trackings = relationship("EyeTracking", back_populates="handover")


    def to_dict(self):
        return {
            "handover_id": self.handover_id,
            "grasped_object": self.grasped_object,
            "giver_grasped_object": self.giver_grasped_object.isoformat() if self.giver_grasped_object else None,
            "receiver_touched_object": self.receiver_touched_object.isoformat() if self.receiver_touched_object else None,
            "receiver_grasped_object": self.receiver_grasped_object.isoformat() if self.receiver_grasped_object else None,
            "giver_released_object": self.giver_released_object.isoformat() if self.giver_released_object else None,
            "trial_id": self.trial_id,
            "giver": self.giver,
            "receiver": self.receiver
        }