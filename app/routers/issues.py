from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.issue import Issue
from app.models.user import User
from app.schemas.issue import (
    BulkStatusUpdate,
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueListResponse,
    CSVImportContent,
)
from datetime import datetime
from typing import Optional, Literal
import csv
import io

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


@router.post("/bulk-status", status_code=status.HTTP_200_OK)
def bulk_update_status(
    bulk_status_update: BulkStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        issues = (
            db.query(Issue)
            .filter(Issue.id.in_(bulk_status_update.issue_ids))
            .with_for_update()
            .all()
        )

        if len(issues) != len(bulk_status_update.issue_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Some issues not found",
            )

        for issue in issues:
            if bulk_status_update.status == "closed" and issue.status != "resolved":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Issue ID {issue.id} must be resolved before closing",
                )

            issue.status = bulk_status_update.status

            if bulk_status_update.status == "resolved":
                issue.resolved_at = datetime.utcnow()
            elif (
                bulk_status_update.status == "open"
                or bulk_status_update.status == "in_progress"
            ):
                issue.resolved_at = None

            issue.version += 1

        db.commit()
        total = len(issues)
        return {
            "message": "Bulk status update successful",
            "updated_count": total,
            "issue_ids": bulk_status_update.issue_ids,
        }

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bulk update failed, transaction rolled back",
        )


@router.post(
    "/import-csv", response_model=CSVImportContent, status_code=status.HTTP_201_CREATED
)
def import_issues_from_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Please upload a CSV file.",
        )

    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload a CSV file.",
        )

    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))

    total_rows = 0
    created_issues = 0
    failed_rows = 0
    errors = []

    allowed_priorities = {"low", "medium", "high", "critical"}

    for index, row in enumerate(reader, start=1):
        total_rows += 1
        try:
            title = row.get("title")
            if not title or not (5 <= len(title) <= 200):
                raise ValueError("Title must be between 5 and 200 characters.")

            description = row.get("description", "")

            priority = row.get("priority")
            if priority not in allowed_priorities:
                raise ValueError(
                    f"Invalid priority '{priority}'. Must be one of {allowed_priorities}."
                )

            assignee_id = row.get("assignee_id")
            if assignee_id:
                assignee = db.query(User).filter(User.id == int(assignee_id)).first()
                if not assignee:
                    raise ValueError(f"Assignee with ID {assignee_id} does not exist.")

            db_issue = Issue(
                title=title,
                description=description,
                priority=priority,
                assignee_id=int(assignee_id) if assignee_id else None,
                status="open",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(db_issue)
            db.commit()
            created_issues += 1

        except ValueError as e:
            db.rollback()
            failed_rows += 1
            errors.append(
                {
                    "row": index,
                    "error": str(e),
                }
            )

    return CSVImportContent(
        total_rows=total_rows,
        created_issues=created_issues,
        failed_rows=failed_rows,
        errors=errors,
    )
