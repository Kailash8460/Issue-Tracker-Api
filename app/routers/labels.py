from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.issue import Issue
from app.models.label import Label
from app.schemas.label import IssueLabelUpdate, LabelListResponse
from app.utils.timeline import log_issue_event

router = APIRouter(
    prefix="/issues/{issue_id}/labels",
    tags=["labels"],
)


@router.put("/", response_model=LabelListResponse, status_code=status.HTTP_200_OK)
def replace_issue_labels(
    issue_id: int,
    label_update: IssueLabelUpdate,
    db: Session = Depends(get_db),
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found",
        )

    try:
        old_labels_str = ", ".join([label.name for label in issue.labels])
        new_labels = []
        for label_name in label_update.labels:
            normalized_name = label_name.strip().lower()
            label = db.query(Label).filter(Label.name == normalized_name).first()
            if not label:
                label = Label(name=normalized_name)
                db.add(label)
                db.flush()
            new_labels.append(label)
        issue.labels = new_labels
        new_labels_str = ", ".join(label.name for label in new_labels)
        log_issue_event(
            db_session=db,
            issue_id=issue_id,
            event_type="labels updated",
            old_value=old_labels_str,
            new_value=new_labels_str,
        )
        db.commit()
        db.refresh(issue)
        return LabelListResponse(total=len(issue.labels), labels=issue.labels)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update labels",
        )
