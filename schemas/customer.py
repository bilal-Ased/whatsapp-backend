from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

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
    status: str
    created_at: Optional[date]