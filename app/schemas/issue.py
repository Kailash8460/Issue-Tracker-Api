from pydantic import BaseModel, Field
from typing import Optional


class IssueCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = Field("low")
    assignee_id: Optional[int] = None
