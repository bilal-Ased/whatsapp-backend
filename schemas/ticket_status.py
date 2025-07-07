# schemas/ticket_status.py
from pydantic import BaseModel, Field
from typing import Optional
from .base import BaseSchema


class TicketStatusBase(BaseModel):
    """Base ticket status schema"""
    status_name: str
    description: Optional[str] = None
    is_active: bool = True


class TicketStatusModel(TicketStatusBase, BaseSchema):
    """Ticket status model for reading data"""
    id: Optional[int] = None


class TicketStatusCreate(TicketStatusBase):
    """Ticket status model for creating new records"""
    status_name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    is_active: bool = True


class TicketStatusUpdate(BaseModel):
    """Ticket status model for updating existing records"""
    status_name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None