# schemas/ticket.py
from pydantic import BaseModel, Field
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from .base import BaseSchema

# Import for type checking to avoid circular imports
if TYPE_CHECKING:
    from .customer import CustomerModel
    from .ticket_category import TicketCategoryModel
    from .sub_category import SubCategoryModel
    from .disposition import DispositionModel
    from .ticket_status import TicketStatusModel
    from .file_upload import FileUploadModel


class TicketBase(BaseModel):
    """Base ticket schema"""
    customer_id: int
    ticket_category_id: int
    sub_category_id: int
    disposition_id: int
    ticket_status_id: int
    notes: Optional[str] = None
    assigned_to: Optional[int] = None
    created_by: Optional[int] = None


class TicketModel(TicketBase, BaseSchema):
    """Ticket model for reading data"""
    id: Optional[int] = None
    resolved_at: Optional[datetime] = None


class TicketCreate(TicketBase):
    """Ticket model for creating new records"""
    customer_id: int = Field(..., gt=0)
    ticket_category_id: int = Field(..., gt=0)
    sub_category_id: int = Field(..., gt=0)
    disposition_id: int = Field(..., gt=0)
    ticket_status_id: int = Field(..., gt=0)
    notes: Optional[str] = None
    assigned_to: Optional[int] = Field(None, gt=0)
    created_by: Optional[int] = Field(None, gt=0)


class TicketUpdate(BaseModel):
    """Ticket model for updating existing records"""
    customer_id: Optional[int] = Field(None, gt=0)
    ticket_category_id: Optional[int] = Field(None, gt=0)
    sub_category_id: Optional[int] = Field(None, gt=0)
    disposition_id: Optional[int] = Field(None, gt=0)
    ticket_status_id: Optional[int] = Field(None, gt=0)
    notes: Optional[str] = None
    assigned_to: Optional[int] = Field(None, gt=0)
    created_by: Optional[int] = Field(None, gt=0)
    resolved_at: Optional[datetime] = None


class TicketWithRelations(TicketModel):
    """Ticket model with all related entities"""
    customer: Optional['CustomerModel'] = None
    ticket_category: Optional['TicketCategoryModel'] = None
    sub_category: Optional['SubCategoryModel'] = None
    disposition: Optional['DispositionModel'] = None
    ticket_status: Optional['TicketStatusModel'] = None
    attachments: List['FileUploadModel'] = []
    
    class Config:
        orm_mode = True