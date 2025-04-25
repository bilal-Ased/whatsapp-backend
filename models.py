from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Boolean, Date, UniqueConstraint,UUID,JSON,CHAR,Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base  # Import Base from database.py
from sqlalchemy.sql import func
import uuid


class CustomersTable(Base):
    __tablename__ = "customers_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100))
    middle_name = Column(String(100))
    last_name = Column(String(100))
    mobile_number = Column(String(20), unique=True)  # to allow FK
    alternate_phone_number = Column(String(20))
    identification_no = Column(String(255), unique=True)
    account_number = Column(String(255))
    branch_name = Column(String(255))
    email = Column(String(200))
    secondary_email = Column(String(200))
    branch_code = Column(String(100))
    cif = Column(String(100))
    age = Column(Integer)
    gender = Column(String(20))
    has_fdr = Column(Boolean)
    status = Column(String(50))
    nationality = Column(String(100))
    physical_address = Column(String(255))
    postal_address = Column(String(255))
    date_of_birth = Column(Date)
    status = Column(String(255),default ="1" )

    mobile_banking_data = relationship(
        "MobileBankingData",
        back_populates="customer",
        cascade="all, delete-orphan",
        foreign_keys="MobileBankingData.customer_id"
    )

    credit_card_data = relationship(
        "CreditCardData",
        back_populates="customer",
        cascade="all, delete-orphan",
        foreign_keys="CreditCardData.customer_id"
    )

    tickets = relationship("Tickets", back_populates="customer") 

class MobileBankingData(Base):
    __tablename__ = "mobile_banking_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers_table.id"), nullable=False)
    identification_no = Column(String(255), ForeignKey("customers_table.identification_no"), nullable=False)
    mobile_number = Column(String(20))  # optionally NULL
    pinstatus = Column(String(50))
    account_number = Column(String(255))
    bank_branch_code = Column(String(255))
    pin_suppress = Column(Boolean)
    bank_branch_name = Column(String(255))

    customer = relationship(
        "CustomersTable",
        back_populates="mobile_banking_data",
        foreign_keys=[customer_id]
    )

    __table_args__ = (
        UniqueConstraint("customer_id", "identification_no", "mobile_number", name="uq_customer_identification_mobile"),
    )



class CreditCardData(Base):
    __tablename__ = "credit_card_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers_table.id"), nullable=False)
    identification_no = Column(String(255), ForeignKey("customers_table.identification_no"), nullable=False)
    mobile_number = Column(String(20))
    card_number = Column(String(255))
    cif = Column(String(255))
    card_limit = Column(Integer)
    card_status = Column(String(50))
    
    customer = relationship(
        "CustomersTable",
        back_populates="credit_card_data",
        foreign_keys=[customer_id]
    )

    __table_args__ = (
        UniqueConstraint("customer_id", "identification_no", "mobile_number", name="uq_customer_identification_mobile"),
    )


class TicketTypes(Base):
    __tablename__ = "ticket_types"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    status = Column(String(255),default ="1" )
    created_at = Column(DateTime(timezone=True), server_default=func.now())



class ProductTypes(Base):
    __tablename__ = "product_types"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    status = Column(String(255), default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    ticket_categories = relationship("TicketCategories", back_populates="product_type")
    resolution_types = relationship("ResolutionTypes", back_populates="product_type")


class ResolutionTypes(Base):
    __tablename__ = "resolution_types"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    status = Column(String(255), default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    product_type_id = Column(Integer, ForeignKey("product_types.id"))
    product_type = relationship("ProductTypes", back_populates="resolution_types")

      
    
class TicketCategories(Base):
    __tablename__ = "ticket_categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    product_type_id = Column(Integer, ForeignKey("product_types.id"), nullable=False)  # Link to product type
    status = Column(String(255),default ="1" )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

   # Relationships
    product_type = relationship("ProductTypes", back_populates="ticket_categories")
    
 

class TicketPriority(Base):
    __tablename__ = "ticket_statuses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    status = Column(String(255), default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RootCause(Base):
    __tablename__ = "root_cause"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_category_id = Column(Integer, ForeignKey("ticket_categories.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(255), default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    
class RootCauseOwner(Base):
    __tablename__ = "root_cause_owner"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_category_id = Column(Integer, ForeignKey("ticket_categories.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(255), default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    



class Tickets(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers_table.id"), nullable=False) 
    product_type_id = Column(Integer, ForeignKey("product_types.id"), nullable=False)
    ticket_category_id = Column(Integer, ForeignKey("ticket_categories.id"), nullable=False)
    resolution_type_id = Column(Integer, ForeignKey("resolution_types.id"), nullable=True)
    root_cause_id = Column(Integer, ForeignKey("root_cause.id"), nullable=True)
    root_cause_owner_id = Column(Integer, ForeignKey("root_cause_owner.id"), nullable=True)
    priority_id = Column(Integer, ForeignKey("ticket_statuses.id"), nullable=False)

    # Optional extra fields
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("CustomersTable", back_populates="tickets")
    ticket_type = relationship("TicketTypes")
    product_type = relationship("ProductTypes")
    ticket_category = relationship("TicketCategories")
    resolution_type = relationship("ResolutionTypes")
    root_cause = relationship("RootCause")
    root_cause_owner = relationship("RootCauseOwner")
    priority = relationship("TicketPriority")
    

class Emails(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nylas_id = Column(String(255), unique=True, nullable=False)  # Corrected this line
    thread_id = Column(String(255))
    subject = Column(Text)
    snippet = Column(Text)
    from_name = Column(String(255))
    from_email = Column(String(255))
    to_email = Column(String(255))
    grant_id = Column(CHAR(36), default=lambda: str(uuid.uuid4()))
    starred = Column(Boolean, default=False)
    unread = Column(Boolean, default=True)
    folders = Column(JSON)
    date = Column(DateTime)
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
    move_in_date = Column(Date, nullable=False)
    lease_end_date = Column(Date)
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
    address = Column(String(255), nullable=False)  # Missing from your example
    unit_number = Column(String(20))
    bedrooms = Column(Integer)  # Changed from int to Integer
    monthly_rent = Column(Numeric(10, 2), nullable=False)  # Fixed typo in "monthy_rent" and added precision
    
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
        return f"<Payment(payment_id={self.payment_id}, amount={self.amount}, status={self.payment_status})>"


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
        return f"<PaymentSchedule(schedule_id={self.schedule_id}, due_date={self.due_date}, amount={self.amount_due})>"