# schemas/ticket_category.py
from pydantic import BaseModel, Field
from typing import Optional, List
from .base import BaseSchema
from schemas.sub_category import SubCategoryModel


class TicketCategoryBase(BaseModel):
    """Base ticket category schema"""
    category_name: str
    is_active: bool = True


class TicketCategoryModel(TicketCategoryBase, BaseSchema):
    """Ticket category model for reading data"""
    id: Optional[int] = None


class TicketCategoryCreate(TicketCategoryBase):
    """Ticket category model for creating new records"""
    category_name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class TicketCategoryUpdate(BaseModel):
    """Ticket category model for updating existing records"""
    category_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class TicketCategoryWithSubCategories(TicketCategoryModel):
    """Ticket category model with sub-categories"""
    sub_categories: List['SubCategoryModel'] = []
    
    class Config:
        orm_mode = True