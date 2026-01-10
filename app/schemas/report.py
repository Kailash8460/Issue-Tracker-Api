from pydantic import BaseModel
from typing import Optional


class TopAssigneesReport(BaseModel):
    assignee_id: int
    assignee_name: Optional[str] = None
    issue_count: int

    class Config:
        from_attributes = True


class AverageLatencyReport(BaseModel):
    average_latency_hours: Optional[float]

    class Config:
        from_attributes = True
