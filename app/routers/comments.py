from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc, func
from app.database import get_db
from app.models.comment import Comment
from app.models.issue import Issue
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentListResponse
from typing import Optional, Literal
from datetime import datetime

router = APIRouter(
    prefix="/issues/{issue_id}/comments",
    tags=["comments"],
)


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    issue_id: int, comment: CommentCreate, db: Session = Depends(get_db)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )

    author = db.query(User).filter(User.id == comment.author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author user not found",
        )

    db_comment = Comment(
        content=comment.content,
        issue_id=issue_id,
        author_id=comment.author_id,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.get(
    "/",
    response_model=CommentListResponse,
    status_code=status.HTTP_200_OK,
)
def list_comments(
    issue_id: int,
    author_id: Optional[int] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: Literal["created_at"] = Query("created_at"),
    sort_order: Literal["asc", "desc"] = Query("desc"),
    db: Session = Depends(get_db),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )

    query = db.query(Comment).filter(Comment.issue_id == issue_id)

    if author_id is not None:
        query = query.filter(Comment.author_id == author_id)

    if created_after is not None:
        query = query.filter(Comment.created_at >= created_after)

    if created_before is not None:
        query = query.filter(Comment.created_at <= created_before)

    total = query.count()
    sort_column = getattr(Comment, sort_by)
    query = query.order_by(
        asc(sort_column) if sort_order == "asc" else desc(sort_column)
    )
    offset = (page - 1) * page_size
    comments = query.offset(offset).limit(page_size).all()
    db_comment = CommentListResponse(
        total=total, page=page, page_size=page_size, comments=comments
    )
    return db_comment


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
)
def get_comment_by_id(issue_id: int, comment_id: int, db: Session = Depends(get_db)):
    db_comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.issue_id == issue_id)
        .first()
    )
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    return db_comment
