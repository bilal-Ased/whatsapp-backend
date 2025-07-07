from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Boolean,BigInteger,text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base  # Import Base from database.py
from sqlalchemy.sql import func
import uuid
from sqlalchemy import JSON  # Import JSON instead of JSONB



class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(250), unique=True, index=True)
    email = Column(String(250), unique=True, index=True) 
    phone = Column(String(250), unique=True)  
    hashed_password = Column(String(200))
    status = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    assigned_tickets = relationship("Ticket", foreign_keys="Ticket.assigned_to", back_populates="assigned_user")
    created_tickets = relationship("Ticket", foreign_keys="Ticket.created_by", back_populates="created_by_user")
    uploaded_files = relationship("FileUpload", back_populates="user")



class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(250), index=True)
    last_name = Column(String(250), index=True)
    mobile_number = Column(String(250), unique=True, index=True)  
    email_address = Column(String(200), unique=True)
    alternative_mobile_number = Column(String(250), unique=True, index=True)  
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    tickets = relationship("Ticket", back_populates="customer")

class TicketStatus(Base):
    __tablename__ = "ticket_statuses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    status_name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tickets = relationship("Ticket", back_populates="ticket_status")

class TicketCategory(Base):
    __tablename__ = "ticket_categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    sub_categories = relationship("SubCategory", back_populates="ticket_category")
    tickets = relationship("Ticket", back_populates="ticket_category")



class SubCategory(Base):
    __tablename__ = "sub_categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_category_id = Column(Integer, ForeignKey("ticket_categories.id"), nullable=False, index=True)
    sub_category_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    ticket_category = relationship("TicketCategory", back_populates="sub_categories")
    dispositions = relationship("Disposition", back_populates="sub_category")
    tickets = relationship("Ticket", back_populates="sub_category")



class Disposition(Base):
    __tablename__ = "dispositions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sub_category_id = Column(Integer, ForeignKey("sub_categories.id"), nullable=False, index=True)
    disposition_name = Column(String(100), nullable=False)
    disposition_description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    sub_category = relationship("SubCategory", back_populates="dispositions")
    tickets = relationship("Ticket", back_populates="disposition")


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    ticket_category_id = Column(Integer, ForeignKey("ticket_categories.id"), nullable=False, index=True)
    sub_category_id = Column(Integer, ForeignKey("sub_categories.id"), nullable=False, index=True)
    disposition_id = Column(Integer, ForeignKey("dispositions.id"), nullable=False, index=True)
    ticket_status_id = Column(Integer, ForeignKey("ticket_statuses.id"), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    attachments = relationship(
        "FileUpload",
        primaryjoin="and_(Ticket.id == foreign(FileUpload.related_id), FileUpload.related_table == 'tickets')",
        viewonly=True
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    customer = relationship("Customer", back_populates="tickets")
    ticket_category = relationship("TicketCategory", back_populates="tickets")
    sub_category = relationship("SubCategory", back_populates="tickets")
    disposition = relationship("Disposition", back_populates="tickets")
    ticket_status = relationship("TicketStatus", back_populates="tickets")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    created_by_user = relationship("User", foreign_keys=[created_by])


class FileUpload(Base):
    __tablename__ = "file_uploads"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    related_table = Column(String(100), nullable=True)  # Which table this file belongs to
    related_id = Column(Integer, nullable=True)  # ID of the related record
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="uploaded_files")


class EmailTemplate(Base):
    __tablename__ = "email_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    template_name = Column(String(100), unique=True, nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    email_logs = relationship("EmailLog", back_populates="email_template")

class EmailLog(Base):
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email_template_id = Column(Integer, ForeignKey("email_templates.id"), nullable=False, index=True)
    recipient_email = Column(String(255), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending, sent, failed
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    email_template = relationship("EmailTemplate", back_populates="email_logs")



class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")

