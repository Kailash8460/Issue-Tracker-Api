from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.issue import Issue
from app.models.user import User
from app.schemas.issue import IssueCreate, IssueUpdate, IssueResponse, IssueListResponse
from datetime import datetime
from typing import Optional, Literal

router = APIRouter(
    prefix="/issues",
    tags=["issues"],
)


@router.post("/", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    if issue.assignee_id:
        user = db.query(User).filter(User.id == issue.assignee_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee user not found",
            )

    db_issue = Issue(
        title=issue.title,
        description=issue.description,
        priority=issue.priority or "low",
        assignee_id=issue.assignee_id,
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue


@router.patch(
    "/{issue_id}", response_model=IssueResponse, status_code=status.HTTP_200_OK
)
def update_issue(issue_id: int, issue: IssueUpdate, db: Session = Depends(get_db)):

    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not db_issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )

    if issue.version != db_issue.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Version conflict: Issue has been modified by another process",
        )

    if issue.title is not None:
        db_issue.title = issue.title

    if issue.description is not None:
        db_issue.description = issue.description

    if issue.status is not None:
        db_issue.status = issue.status
        if issue.status == "resolved":
            db_issue.resolved_at = datetime.utcnow()
        elif issue.status != "resolved":
            db_issue.resolved_at = None

    if issue.priority is not None:
        db_issue.priority = issue.priority

    if issue.assignee_id is not None:
        user = db.query(User).filter(User.id == issue.assignee_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee user not found",
            )
        db_issue.assignee_id = issue.assignee_id

    db_issue.version += 1

    db.commit()
    db.refresh(db_issue)
    return db_issue


@router.get("/{issue_id}", response_model=IssueResponse, status_code=status.HTTP_200_OK)
def get_issue_by_id(issue_id: int, db: Session = Depends(get_db)):
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )
    return db_issue


@router.get("/", response_model=IssueListResponse, status_code=status.HTTP_200_OK)
def get_issue(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assignee_id: Optional[int] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    updated_after: Optional[datetime] = Query(None),
    updated_before: Optional[datetime] = Query(None),
    resolved: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: Literal["created_at", "updated_at", "priority", "status"] = Query(
        "created_at"
    ),
    sort_order: Literal["asc", "desc"] = Query("desc"),
    db: Session = Depends(get_db),
):
    query = db.query(Issue)

    if status:
        query = query.filter(Issue.status == status)

    if priority:
        query = query.filter(Issue.priority == priority)

    if assignee_id:
        query = query.filter(Issue.assignee_id == assignee_id)

    if created_after:
        query = query.filter(Issue.created_at >= created_after)

    if created_before:
        query = query.filter(Issue.created_at <= created_before)

    if updated_after:
        query = query.filter(Issue.updated_at >= updated_after)

    if updated_before:
        query = query.filter(Issue.updated_at <= updated_before)

    if resolved is not None:
        if resolved:
            query = query.filter(Issue.resolved_at.isnot(None))
        else:
            query = query.filter(Issue.resolved_at.is_(None))

    # total = query.with_entities(func.count()).scalar()
    total = query.count()
    sort_column = getattr(Issue, sort_by)
    query = query.order_by(
        asc(sort_column) if sort_order == "asc" else desc(sort_column)
    )
    offset = (page - 1) * page_size
    issues = query.offset(offset).limit(page_size).all()
    db_issue = IssueListResponse(
        total=total,
        page=page,
        page_size=page_size,
        issues=issues,
    )
    return db_issue
