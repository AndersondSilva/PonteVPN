from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models import User, Base
from app.routers.auth import get_current_user_dep
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column

router = APIRouter(prefix="/feedback", tags=["feedback"])

class FeedbackModel(Base):
    __tablename__ = "feedback"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(50)) # bug, feature, general
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[func.now()] = mapped_column(DateTime(timezone=True), server_default=func.now())

class FeedbackCreate(BaseModel):
    type: str
    content: str

@router.post("")
async def submit_feedback(
    body: FeedbackCreate,
    user: Optional[User] = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    # This is a bit tricky because Base.metadata.create_all might not have run for this new table
    # But in the startup event of main.py it should work if we import it there.
    
    new_feedback = FeedbackModel(
        user_id=user.id if user else None,
        type=body.type,
        content=body.content
    )
    db.add(new_feedback)
    await db.commit()
    return {"message": "Feedback recebido com sucesso. Obrigado!"}
