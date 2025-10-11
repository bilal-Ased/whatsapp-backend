from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Boolean, Date, UniqueConstraint,UUID,JSON,CHAR,Numeric,BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base  # Import Base from database.py
from sqlalchemy.sql import func
import uuid



class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(250), unique=True, index=True)
    email = Column(String(250), unique=True, index=True)  # Ensure email is unique [[3]]
    phone = Column(String(250), unique=True)  # Optional: Remove `unique=True` if not needed
    hashed_password = Column(String(200))
    status = Column(Boolean,default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    



class Tenants(Base):
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    emergency_contact = Column(String(100))
    active_status = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    leases = relationship("Leases", back_populates="tenant")
    payments = relationship("Payments", back_populates="tenant")
    
    def __repr__(self):
        return f"<Tenant(tenant_id={self.tenant_id}, name={self.first_name} {self.last_name})>"
    

    

class Properties(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    property_name = Column(String(255))
    address = Column(String(255), nullable=False)
    unit_number = Column(String(20), unique=True, nullable=False) 
    bedrooms = Column(Integer)
    status = Column(Integer, default=1)
    monthly_rent = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    leases = relationship("Leases", back_populates="property")
    

class Leases(Base):
    __tablename__ = "leases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    monthly_rent = Column(Numeric(10, 2), nullable=False)
    deposit = Column(Numeric(10, 2), nullable=False)
    lease_document = Column(String(255))
    status = Column(Enum("active", "expired", "terminated", name="lease_status"), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    tenant = relationship("Tenants", back_populates="leases")
    property = relationship("Properties", back_populates="leases")
    payments = relationship("Payments", back_populates="lease")
    payment_schedules = relationship("PaymentSchedule", back_populates="lease")
    
    def __repr__(self):
        return f"<Lease(lease_id={self.lease_id}, tenant_id={self.tenant_id}, property_id={self.property_id})>"





class Payments(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    lease_id = Column(Integer, ForeignKey("leases.id"), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(Enum("cash", "check", "bank_transfer", "credit_card", "other", name="payment_method_enum"), nullable=False)
    payment_status = Column(Enum("pending", "completed", "failed", name="payment_status_enum"), default="pending")
    transaction_reference = Column(String(100))
    late_fee = Column(Numeric(10, 2), default=0.00)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenants", back_populates="payments")
    lease = relationship("Leases", back_populates="payments")
    payment_schedule = relationship("PaymentSchedule", back_populates="payment", uselist=False)
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status={self.payment_status})>"


class PaymentSchedule(Base):
    __tablename__ = "payment_schedule"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    lease_id = Column(Integer, ForeignKey("leases.id"), nullable=False)
    due_date = Column(Date, nullable=False)
    amount_due = Column(Numeric(10, 2), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"))
    status = Column(Enum("pending", "paid", "overdue", name="schedule_status_enum"), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    lease = relationship("Leases", back_populates="payment_schedules")
    payment = relationship("Payments", back_populates="payment_schedule")
    
    def __repr__(self):
        return f"<PaymentSchedule(id={self.id}, due_date={self.due_date}, amount={self.amount_due})>"

    
    

class Email(Base):
    __tablename__ = "emails"

    id = Column(String(255), primary_key=True)  # Nylas message ID
    thread_id = Column(String(255), index=True)
    grant_id = Column(String(255), nullable=False, index=True)
    subject = Column(Text)
    snippet = Column(String(500))  # Short preview
    date = Column(DateTime, index=True)
    folder = Column(String(100), index=True)
    unread = Column(Boolean, default=False, index=True)
    starred = Column(Boolean, default=False)
    has_attachments = Column(Boolean, default=False)
    attachment_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    participants = relationship("EmailParticipant", back_populates="email", cascade="all, delete-orphan")
    attachments = relationship("EmailAttachment", back_populates="email", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Email(id='{self.id}', subject='{self.subject}', date='{self.date}')>"

class EmailParticipant(Base):
    __tablename__ = "email_participants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email_id = Column(String(255), ForeignKey("emails.id", ondelete="CASCADE"), index=True)
    participant_type = Column(Enum('from', 'to', 'cc', 'bcc', 'reply_to', name='participant_type_enum'), index=True)
    email_address = Column(String(255), index=True)
    display_name = Column(String(255))

    # Relationships
    email = relationship("Email", back_populates="participants")

    def __repr__(self):
        return f"<EmailParticipant(type='{self.participant_type}', address='{self.email_address}')>"


class EmailAttachment(Base):
    __tablename__ = "email_attachments"

    id = Column(String(255), primary_key=True)  # Nylas attachment ID
    email_id = Column(String(255), ForeignKey("emails.id", ondelete="CASCADE"), index=True)
    filename = Column(String(500))
    content_type = Column(String(100), index=True)
    size = Column(BigInteger)
    is_inline = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    email = relationship("Email", back_populates="attachments")

    def __repr__(self):
        return f"<EmailAttachment(filename='{self.filename}', size={self.size})>"



class WhatsAppContact(Base):
    __tablename__ = "whatsapp_contacts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    wa_id = Column(String(50), unique=True, nullable=False, index=True)  # WhatsApp ID (phone number)
    profile_name = Column(String(100))
    phone_number = Column(String(20))
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    messages = relationship("WhatsAppMessage", back_populates="contact")
    
    def __repr__(self):
        return f"<WhatsAppContact(wa_id={self.wa_id}, name={self.profile_name})>"


class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(200), unique=True, nullable=False, index=True)  # WhatsApp message ID
    contact_id = Column(Integer, ForeignKey("whatsapp_contacts.id"), nullable=False)
    from_number = Column(String(50), nullable=False)
    to_number = Column(String(50))  # Your business number
    message_type = Column(String(20), nullable=False)  # text, image, video, document, etc.
    message_body = Column(Text)
    media_url = Column(String(500))
    media_mime_type = Column(String(100))
    timestamp = Column(DateTime(timezone=True), nullable=False)
    is_read = Column(Boolean, default=False)
    direction = Column(String(10), default="inbound")  # inbound or outbound
    status = Column(String(20), default="received")  # received, sent, delivered, read, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    contact = relationship("WhatsAppContact", back_populates="messages")
    
    def __repr__(self):
        return f"<WhatsAppMessage(id={self.id}, from={self.from_number}, type={self.message_type})>"