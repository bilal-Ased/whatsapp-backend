from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Literal, Dict, Any
from datetime import date, datetime
import uuid
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from .base import BaseSchema

# User Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=250)
    email: EmailStr
    phone: str = Field(..., max_length=250)
    password: str = Field(..., min_length=6)
    status: bool = True

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=250)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=250)
    password: Optional[str] = Field(None, min_length=6)
    status: Optional[bool] = None

class UserModel(BaseModel):
    id: int
    username: str
    email: str
    phone: str
    status: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str




class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    mobile_number: str
    email_address: str
    alternative_mobile_number: Optional[str] = None
    full_name: str 
    class Config:
        from_attributes = True



class CustomerModel(CustomerBase, BaseSchema):
    """Customer model for reading data"""
    id: Optional[int] = None


class CustomerCreate(CustomerBase):
    """Customer model for creating new records"""
    first_name: str = Field(..., min_length=1, max_length=250)
    last_name: str = Field(..., min_length=1, max_length=250)
    mobile_number: str = Field(..., max_length=250)
    email_address: EmailStr
    alternative_mobile_number: Optional[str] = Field(None, max_length=250)


class CustomerUpdate(BaseModel):
    """Customer model for updating existing records"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=250)
    last_name: Optional[str] = Field(None, min_length=1, max_length=250)
    mobile_number: Optional[str] = Field(None, max_length=250)
    email_address: Optional[EmailStr] = None
    alternative_mobile_number: Optional[str] = Field(None, max_length=250)


class CustomerWithTickets(CustomerModel):
    """Customer model with related tickets"""
    tickets: List['TicketModel'] = []
    
    class Config:
        orm_mode = True
