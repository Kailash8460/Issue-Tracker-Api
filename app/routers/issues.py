from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.issue import Issue
from app.models.user import User
from app.schemas.issue import IssueCreate, IssueUpdate, IssueResponse
from datetime import datetime

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
