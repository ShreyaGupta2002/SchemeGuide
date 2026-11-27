from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from .database import Base


class FeedbackRecord(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    scheme_version_id = Column(Integer, nullable=False)
    scheme_name = Column(String(255), nullable=False)
    problem_description = Column(Text, nullable=False)
    correct_information = Column(Text, nullable=True)
    official_source_url = Column(String(500), nullable=True)
    status = Column(String(20), default="open")  # open, resolved, dismissed
    created_at = Column(DateTime, server_default=func.now())


# Pydantic schemas
class FeedbackCreate(BaseModel):
    scheme_version_id: int
    scheme_name: str
    problem_description: str
    correct_information: str | None = None
    official_source_url: str | None = None


class FeedbackResponse(BaseModel):
    id: int
    scheme_version_id: int
    scheme_name: str
    problem_description: str
    correct_information: str | None
    official_source_url: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
