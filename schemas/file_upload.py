# schemas/file_upload.py
from pydantic import BaseModel, Field
from typing import Optional
from .base import BaseSchema


class FileUploadBase(BaseModel):
    """Base file upload schema"""
    original_filename: str
    stored_filename: str
    file_path: str
    file_size: int
    mime_type: str
    file_hash: Optional[str] = None
    uploaded_by: Optional[int] = None
    related_table: Optional[str] = None
    related_id: Optional[int] = None
    is_active: bool = True


class FileUploadModel(FileUploadBase, BaseSchema):
    """File upload model for reading data"""
    id: Optional[int] = None


class FileUploadCreate(FileUploadBase):
    """File upload model for creating new records"""
    original_filename: str = Field(..., min_length=1, max_length=255)
    stored_filename: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=500)
    file_size: int = Field(..., gt=0)
    mime_type: str = Field(..., min_length=1, max_length=100)
    file_hash: Optional[str] = Field(None, max_length=64)
    uploaded_by: Optional[int] = Field(None, gt=0)
    related_table: Optional[str] = Field(None, max_length=100)
    related_id: Optional[int] = Field(None, gt=0)
    is_active: bool = True


class FileUploadUpdate(BaseModel):
    """File upload model for updating existing records"""
    original_filename: Optional[str] = Field(None, min_length=1, max_length=255)
    stored_filename: Optional[str] = Field(None, min_length=1, max_length=255)
    file_path: Optional[str] = Field(None, min_length=1, max_length=500)
    file_size: Optional[int] = Field(None, gt=0)
    mime_type: Optional[str] = Field(None, min_length=1, max_length=100)
    file_hash: Optional[str] = Field(None, max_length=64)
    uploaded_by: Optional[int] = Field(None, gt=0)
    related_table: Optional[str] = Field(None, max_length=100)
    related_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None