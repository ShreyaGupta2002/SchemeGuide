from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .database import get_db
from .models import FeedbackRecord, FeedbackCreate, FeedbackResponse

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse, status_code=201)
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    record = FeedbackRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/feedback", response_model=List[FeedbackResponse])
def list_feedback(status: str = None, db: Session = Depends(get_db)):
    query = db.query(FeedbackRecord)
    if status:
        query = query.filter(FeedbackRecord.status == status)
    return query.order_by(FeedbackRecord.created_at.desc()).all()


@router.get("/feedback/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    record = db.query(FeedbackRecord).filter(FeedbackRecord.id == feedback_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return record


@router.patch("/feedback/{feedback_id}/resolve", response_model=FeedbackResponse)
def resolve_feedback(feedback_id: int, db: Session = Depends(get_db)):
    record = db.query(FeedbackRecord).filter(FeedbackRecord.id == feedback_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Feedback not found")
    record.status = "resolved"
    db.commit()
    db.refresh(record)
    return record
