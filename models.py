from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Boolean, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base  # Import Base from database.py
from sqlalchemy.sql import func


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
    status = Column(String(255),default ="1" )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    ticket_categories = relationship("TicketCategories", back_populates="product_type")
    
    
class TicketCategories(Base):
    __tablename__ = "ticket_categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    product_type_id = Column(Integer, ForeignKey("product_types.id"), nullable=False)  # Link to product type
    status = Column(String(255),default ="1" )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

   # Relationships
    product_type = relationship("ProductTypes", back_populates="ticket_categories")
    resolution_types = relationship("ResolutionTypes", back_populates="ticket_category")
    
class ResolutionTypes(Base):
    __tablename__ = "resolution_types"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_category_id = Column(Integer, ForeignKey("ticket_categories.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(255), default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket_category = relationship("TicketCategories", back_populates="resolution_types") 

class TicketPriority(Base):
    __tablename__ = "ticket_statuses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_category_id = Column(Integer, ForeignKey("ticket_categories.id"), nullable=False)
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
    
    # Foreign keys
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
