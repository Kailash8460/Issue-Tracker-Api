from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.issue import Issue
from app.models.user import User
from app.schemas.report import TopAssigneesReport, AverageLatencyReport
from typing import List

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
)


@router.get(
    "/top-assignees",
    response_model=List[TopAssigneesReport],
)
def get_top_assignees(
    limit: int = 100,
    db: Session = Depends(get_db),
):
    results = (
        db.query(
            User.id.label("assignee_id"),
            User.username.label("assignee_name"),
            func.count(Issue.id).label("issue_count"),
        )
        .join(Issue, Issue.assignee_id == User.id)
        .group_by(User.id, User.username)
        .order_by(func.count(Issue.id).desc())
        .limit(limit)
        .all()
    )
    return results


@router.get(
    "/average-latency",
    response_model=AverageLatencyReport,
)
def get_average_latency(
    db: Session = Depends(get_db),
):
    avg_seconds = (
        db.query(func.avg(func.extract("epoch", Issue.resolved_at - Issue.created_at)))
        .filter(Issue.resolved_at.isnot(None))
        .scalar()
    )

    if avg_seconds is None:
        return AverageLatencyReport(average_latency_hours=0)

    avg_hours = round(avg_seconds / 3600, 2)
    return AverageLatencyReport(average_latency_hours=avg_hours or 0)
