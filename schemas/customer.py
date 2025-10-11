from pydantic import BaseModel, EmailStr
from typing import Optional,List,Literal
from datetime import date
import uuid
from datetime import datetime
from decimal import Decimal

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


class TenantModel(BaseModel):
    id: Optional[int] = None  
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    lease_id: Optional[int] = None
    move_in_date: Optional[date] = None
    lease_end_date: Optional[date] = None
    active_status: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class PropertyModel(BaseModel):
    id: Optional[int] = None  # Changed from str to int
    property_name: str
    address: str
    status: str
    unit_number: str
    bedrooms: int 
    status: Optional[str] = "Vacant"
    monthly_rent: Decimal
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    phone: str
    password: str
    status: bool = True
    created_at: Optional[datetime] = None

    
    class Config:
        orm_mode = True
        
        
        
class UserRead(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: str
    password: str
    
class LeaseBase(BaseModel):
    tenant_id: int
    property_id: int
    start_date: date
    end_date: date
    monthly_rent: Decimal
    deposit: Decimal
    lease_document: Optional[str] = None
    status: Optional[str] = "active"

class LeaseCreate(LeaseBase):
    pass

class LeaseOut(LeaseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class LeaseWithDetails(BaseModel):
    id: int  # Changed from str to int
    tenant_id: int  # Changed from str to int
    tenant_name: str
    tenant_phone: str
    tenant_email: Optional[str] = None
    property_name: str
    start_date: date
    end_date: date
    monthly_rent: Decimal
    deposit: Decimal
    lease_document: Optional[str] = None
    status: str

    class Config:
        extra = "ignore"        
        
class EmailAttachmentBase(BaseModel):
    id: str
    filename: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None
    is_inline: Optional[bool] = False
    created_at: Optional[datetime] = None

class EmailAttachmentRead(EmailAttachmentBase):
    class Config:
        orm_mode = True


class EmailParticipantBase(BaseModel):
    participant_type: Literal['from', 'to', 'cc', 'bcc', 'reply_to']
    email_address: Optional[EmailStr] = None
    display_name: Optional[str] = None

class EmailParticipantRead(EmailParticipantBase):
    class Config:
        orm_mode = True


class EmailBase(BaseModel):
    id: str
    thread_id: Optional[str] = None
    grant_id: str
    subject: Optional[str] = None
    snippet: Optional[str] = None
    date: Optional[datetime] = None
    folder: Optional[str] = None
    unread: Optional[bool] = False
    starred: Optional[bool] = False
    has_attachments: Optional[bool] = False
    attachment_count: Optional[int] = 0

class EmailRead(EmailBase):
    attachments: List[EmailAttachmentRead] = []
    participants: List[EmailParticipantRead] = []

    class Config:
        orm_mode = True



class PaymentScheduleBase(BaseModel):
    lease_id: int
    due_date: date
    amount_due: Decimal
    status: Optional[str] = "pending"


class PaymentScheduleCreate(PaymentScheduleBase):
    pass


class PaymentScheduleRead(PaymentScheduleBase):
    id: int
    payment_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ========================
# Payments Schemas
# ========================

class PaymentCreate(BaseModel):
    tenant_id: int
    lease_id: int
    amount: float
    payment_method: str
    transaction_reference: Optional[str] = None
    notes: Optional[str] = None





class PaymentStatusUpdate(BaseModel):
    status: str
    
    
    
    
    
class WhatsAppContactBase(BaseModel):
    wa_id: str
    profile_name: Optional[str] = None
    phone_number: Optional[str] = None

class WhatsAppContactCreate(WhatsAppContactBase):
    pass

class WhatsAppContactRead(WhatsAppContactBase):
    id: int
    is_blocked: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WhatsAppMessageBase(BaseModel):
    message_id: str
    from_number: str
    to_number: Optional[str] = None
    message_type: str
    message_body: Optional[str] = None
    media_url: Optional[str] = None
    timestamp: datetime

class WhatsAppMessageCreate(WhatsAppMessageBase):
    contact_id: int

class WhatsAppMessageRead(WhatsAppMessageBase):
    id: int
    contact_id: int
    is_read: bool
    direction: str
    status: str
    created_at: datetime
    contact: Optional[WhatsAppContactRead] = None

    class Config:
        from_attributes = True


class WebhookPayload(BaseModel):
    profile_name: str
    wa_id: str
    message_id: str
    from_number: str
    timestamp: str
    message_type: str
    message_body: Optional[str] = None
