# schemas/sub_category.py
from pydantic import BaseModel, Field
from typing import Optional, List
from .base import BaseSchema
from schemas.disposition import DispositionModel

class SubCategoryBase(BaseModel):
    """Base sub category schema"""
    ticket_category_id: int
    sub_category_name: str
    is_active: bool = True


class SubCategoryModel(SubCategoryBase, BaseSchema):
    """Sub category model for reading data"""
    id: Optional[int] = None


class SubCategoryCreate(SubCategoryBase):
    """Sub category model for creating new records"""
    ticket_category_id: int = Field(..., gt=0)
    sub_category_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class SubCategoryUpdate(BaseModel):
    """Sub category model for updating existing records"""
    ticket_category_id: Optional[int] = Field(None, gt=0)
    sub_category_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class SubCategoryWithDispositions(SubCategoryModel):
    """Sub-category model with dispositions"""
    dispositions: List['DispositionModel'] = []
    
    class Config:
        orm_mode = True