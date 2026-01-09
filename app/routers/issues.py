from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.issue import Issue
from app.models.user import User
from app.schemas.issue import IssueCreate

router = APIRouter(
    prefix="/issues",
    tags=["issues"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
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
    return {"message": "Issue created successfully", "issue": db_issue}
