from pydantic import BaseModel, EmailStr
from typing import Optional,List,Literal
from datetime import date
import uuid
from datetime import datetime
from decimal import Decimal


class CustomerCreate(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    mobile_number: str
    alternate_phone_number: Optional[str] = None
    identification_no: str
    account_number: str
    branch_name: Optional[str] = None
    email: Optional[EmailStr] = None
    secondary_email: Optional[EmailStr] = None
    branch_code: Optional[str] = None
    cif: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    has_fdr: Optional[bool] = None
    status: Optional[str] = None
    nationality: Optional[str] = None
    physical_address: Optional[str] = None
    postal_address: Optional[str] = None
    date_of_birth: Optional[date] = None
    
    
    

    
    
class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    mobile_number: Optional[str] = None
    alternate_phone_number: Optional[str] = None
    identification_no: Optional[str] = None
    account_number: Optional[str] = None
    branch_name: Optional[str] = None
    email: Optional[EmailStr] = None
    secondary_email: Optional[EmailStr] = None
    branch_code: Optional[str] = None
    cif: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    has_fdr: Optional[bool] = None
    status: Optional[str] = None
    nationality: Optional[str] = None
    physical_address: Optional[str] = None
    postal_address: Optional[str] = None
    date_of_birth: Optional[date] = None


class MobileCustomerData(BaseModel):
    id: int
    customer_id: int
    identification_no: str
    mobile_number: Optional[str] = None
    pinstatus: Optional[str] = None
    account_number: Optional[str] = None
    bank_branch_code: Optional[str] = None
    pin_suppress: Optional[bool] = None
    bank_branch_name: Optional[str] = None

    class Config:
        orm_mode = True    
        
        
        
class CreditCardCustomerData(BaseModel):
    id: int
    customer_id: int
    identification_no: str
    mobile_number: Optional[str] = None
    card_number: Optional[str] = None
    cif: Optional[str] = None
    card_limit: Optional[int] = None
    card_status: Optional[str] = None

    class Config:
        orm_mode = True    

class TicketCreate(BaseModel):
    customer_id: int
    ticket_type_id: int
    product_type_id: int
    ticket_category_id: int
    resolution_type_id: Optional[int] = None
    root_cause_id: Optional[int] = None
    root_cause_owner_id: Optional[int] = None
    priority_id: int
    comments: Optional[str] = None
    
class TicketType(BaseModel):
    name: str
    status: Optional[str] = None
    created_at: Optional[date] = None


class TicketStatus(BaseModel):
    name: str
    status : Optional[str] = None
    created_at: Optional[str]= None
    
class ProductTypeModel(BaseModel):
    name: str
    status : Optional[str] = None
    created_at: Optional[str]= None
    

class ResolutionTypeModel(BaseModel):
    name: str
    status: Optional[str] = None
    created_at: Optional[str] = None
    product_type_id: int
    

class TicketCategoryModel(BaseModel):
    name: str
    status: Optional[str] = None
    created_at: Optional[str] = None
    product_type_id: int


class EmailModel(BaseModel):
    nylas_id: str
    thread_id: Optional[str] = None
    subject: Optional[str] = None
    snippet: Optional[str] = None
    from_name: Optional[str] = None
    from_email: Optional[str] = None
    to_email: Optional[str] = None
    grant_id: Optional[str] = str(uuid.uuid4())  # Default UUID
    starred: Optional[bool] = False
    unread: Optional[bool] = True
    folders: Optional[List[str]] = []
    date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None




class TenantModel(BaseModel):
    id: int 
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    move_in_date: date
    lease_end_date: Optional[date] = None
    active_status: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
class PropertyModel(BaseModel):
    property_name: str
    address: str
    unit_number: str
    bedrooms : int 
    monthly_rent: Decimal
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    phone: str
    status: bool = True
    created_at: Optional[datetime] = None

    
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
