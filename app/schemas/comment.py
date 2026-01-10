from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    author_id: int


class CommentResponse(BaseModel):
    id: int
    content: str
    issue_id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    comments: list[CommentResponse]

    class Config:
        from_attributes = True
