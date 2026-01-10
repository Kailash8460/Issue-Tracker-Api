from pydantic import BaseModel, Field
from typing import Optional, List


class LabelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#(?:[0-9a-fA-F]{3}){1,2}$")


class LabelResponse(BaseModel):
    id: int
    name: str
    color: Optional[str] = None

    class Config:
        from_attributes = True


class LabelListResponse(BaseModel):
    total: int
    labels: List[LabelResponse]

    class Config:
        from_attributes = True


class IssueLabelUpdate(BaseModel):
    labels: List[str] = Field(..., min_items=1)
