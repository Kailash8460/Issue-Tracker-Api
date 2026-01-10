from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class IssueEvent(Base):
    __tablename__ = "issue_events"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    old_value = Column(String(255), nullable=True)
    new_value = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    issue = relationship("Issue", back_populates="events")

    def __repr__(self):
        return f"<IssueEvent(id={self.id}, issue_id={self.issue_id}, event_type='{self.event_type}', created_at={self.created_at})>"
