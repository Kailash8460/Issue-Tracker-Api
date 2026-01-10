from pydantic import BaseModel, Field
from typing import Optional, Literal, List
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


class IssueFilter(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    updated_after: Optional[datetime] = None
    updated_before: Optional[datetime] = None
    resolved: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)
    sort_by: Literal["created_at", "updated_at", "priority", "status"] = "created_at"
    sort_order: Literal["asc", "desc"] = "desc"


class IssueListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    issues: list[IssueResponse]

    class Config:
        from_attributes = True


class BulkStatusUpdate(BaseModel):
    issue_ids: List[int] = Field(..., min_items=1)
    status: Literal["open", "in_progress", "resolved", "closed"]


class CSVImportContent(BaseModel):
    total_rows: int
    created_issues: int
    failed_rows: int
    errors: List[dict]
