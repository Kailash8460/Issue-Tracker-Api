from app.models.issue_event import IssueEvent


def log_issue_event(
    db_session,
    issue_id: int,
    event_type: str,
    old_value: str = None,
    new_value: str = None,
):
    event = IssueEvent(
        issue_id=issue_id,
        event_type=event_type,
        old_value=old_value,
        new_value=new_value,
    )
    db_session.add(event)
