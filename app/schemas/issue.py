from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class IssueCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = Field("low")
    assignee_id: Optional[int] = None


class IssueUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(None)
    priority: Optional[str] = Field(None)
    assignee_id: Optional[int] = None
    version: int


class IssueResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    assignee_id: Optional[int] = None
    version: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
