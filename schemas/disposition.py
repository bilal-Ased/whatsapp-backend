# schemas/disposition.py
from pydantic import BaseModel, Field
from typing import Optional
from .base import BaseSchema


class DispositionBase(BaseModel):
    """Base disposition schema"""
    sub_category_id: int
    disposition_name: str
    disposition_description: Optional[str] = None
    is_active: bool = True


class DispositionModel(DispositionBase, BaseSchema):
    """Disposition model for reading data"""
    id: Optional[int] = None


class DispositionCreate(DispositionBase):
    """Disposition model for creating new records"""
    sub_category_id: int = Field(..., gt=0)
    disposition_name: str = Field(..., min_length=1, max_length=100)
    disposition_description: Optional[str] = None
    is_active: bool = True


class DispositionUpdate(BaseModel):
    """Disposition model for updating existing records"""
    sub_category_id: Optional[int] = Field(None, gt=0)
    disposition_name: Optional[str] = Field(None, min_length=1, max_length=100)
    disposition_description: Optional[str] = None
    is_active: Optional[bool] = None