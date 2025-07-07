from fastapi import FastAPI, Depends, Query, Request
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import joinedload
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from sqlalchemy import or_, func  # Add func import
from security import get_password_hash
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import desc

from utils import get_current_user
from typing import List, Dict, Any, Union
import httpx
from pydantic import BaseModel, EmailStr
from fastapi.responses import JSONResponse
from sqlalchemy import text
from io import StringIO
import csv
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from datetime import date
from decimal import Decimal
import os 
from uuid import uuid4
from fastapi.staticfiles import StaticFiles
import logging
import traceback
from routers import customer  
import json 

app = FastAPI()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# list of customers 

app.include_router(customer.router)


# tickets creation table is here 
# @app.post("/create-ticket-status")
# def create_ticket_status(data: TicketStatusCreate, db: Session = Depends(get_db)):
#     # Exclude auto-generated fields
#     new_ticket_status = TicketStatus(**data.dict(exclude_unset=True))
#     db.add(new_ticket_status)
#     try:
#         db.commit()
#         db.refresh(new_ticket_status)
#     except IntegrityError as e:
#         db.rollback()
#         error_message = str(e.orig)
#         if isinstance(e.orig, Exception):
#             if "unique constraint" in error_message.lower() or "duplicate entry" in error_message.lower():
#                 if "status_name" in error_message.lower():
#                     raise HTTPException(
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                         detail="Status name already exists. Please use a different status name."
#                     )
#             else:
#                 raise HTTPException(
#                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                     detail="An error occurred while creating the ticket status. Please try again."
#                 )

#     return {"message": "New ticket status created", "new_ticket_status_id": new_ticket_status.id}

# @app.post("/create-ticket-category")
# def create_ticket_category(data: TicketCategoryCreate, db: Session = Depends(get_db)):
#     logger.info(f"Received data: {data}")
    
#     try:
#         # Validate field definitions
#         logger.info("Starting field validation...")
#         for field_def in data.field_definitions:
#             if field_def.type == FieldType.SELECT and not field_def.options:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail=f"Field '{field_def.name}' of type SELECT must have options defined."
#                 )
#         logger.info("Field validation completed")
        
#         # Create the category - USE .dict() for Pydantic v1
#         logger.info("Creating category data...")
#         category_data = data.dict(exclude={'field_definitions'})  # ✅ Use .dict()
#         logger.info(f"Category data: {category_data}")
        
#         new_ticket_category = TicketCategory(**category_data)
#         logger.info("TicketCategory object created")
        
#         # Serialize field definitions - USE .dict() for Pydantic v1
#         logger.info("Serializing field definitions...")
#         field_definitions_dict = [field_def.dict() for field_def in data.field_definitions]  # ✅ Use .dict()
#         logger.info(f"Serialized field definitions: {field_definitions_dict}")
        
#         new_ticket_category.field_definitions = field_definitions_dict
#         logger.info("Field definitions assigned to category")
        
#         # Database operations
#         logger.info("Adding to database...")
#         db.add(new_ticket_category)
#         logger.info("Committing transaction...")
#         db.commit()
#         logger.info("Refreshing object...")
#         db.refresh(new_ticket_category)
#         logger.info("Database operations completed successfully")
        
#         return {
#             "message": "New ticket category created", 
#             "new_ticket_category_id": new_ticket_category.id
#         }
        
#     except HTTPException:
#         logger.error("HTTP Exception occurred")
#         raise
#     except IntegrityError as e:
#         logger.error(f"IntegrityError: {e}")
#         db.rollback()
#         if "unique constraint" in str(e.orig).lower() or "duplicate entry" in str(e.orig).lower():
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Category name already exists. Please use a different category name."
#             )
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Database integrity error: {str(e)}"
#         )
#     except Exception as e:
#         logger.error(f"Unexpected error: {e}")
#         logger.error(f"Traceback: {traceback.format_exc()}")
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An unexpected error occurred: {str(e)}"
#         )


# @app.get("/ticket-categories-list", response_model=List[TicketCategoryModel])
# def get_ticket_categories(
#     db: Session = Depends(get_db),
#     search: Optional[str] = Query(None, description="Search by category name or description")
# ):
#     """
#     Get list of ticket categories with optional search
#     """
#     query = db.query(TicketCategory)
    
#     # Apply search filter if provided
#     if search:
#         search_term = f"%{search}%"
#         query = query.filter(
#             or_(
#                 TicketCategory.category_name.ilike(search_term),
#                 TicketCategory.description.ilike(search_term)
#             )
#         )
    
#     categories = query.all()
    
#     # Convert SQLAlchemy models to Pydantic models
#     result = []
#     for category in categories:
#         category_dict = {
#             "id": category.id,
#             "category_name": category.category_name,
#             "description": category.description,
#             "is_active": category.is_active,
#             "field_definitions": category.field_definitions or [],
#             "created_at": category.created_at,
#             "updated_at": category.updated_at
#         }
#         result.append(TicketCategoryModel(**category_dict))
    
#     return result

# @app.get("/ticket-status-list", response_model=List[TicketStatusModel])
# def get_ticket_statuses(
#     db: Session = Depends(get_db),
#     search: Optional[str] = Query(None, description="Search by status name or description")
# ):
#     """
#     Get list of ticket statuses with optional search
#     """
#     query = db.query(TicketStatus)
    
#     # Apply search filter if provided
#     if search:
#         search_term = f"%{search}%"
#         query = query.filter(
#             or_(
#                 TicketStatus.status_name.ilike(search_term),
#                 TicketStatus.description.ilike(search_term)
#             )
#         )
    
#     statuses = query.all()
#     return statuses

# @app.post("/create-ticket")
# def create_ticket(data: TicketCreate, db: Session = Depends(get_db)):
#     # Check if customer exists
#     customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
#     if not customer:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Customer not found."
#         )
    
#     # Check if ticket status exists
#     ticket_status = db.query(TicketStatus).filter(TicketStatus.id == data.ticket_status_id).first()
#     if not ticket_status:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Ticket status not found."
#         )
    
#     # Check if ticket category exists
#     ticket_category = db.query(TicketCategory).filter(TicketCategory.id == data.ticket_category_id).first()
#     if not ticket_category:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Ticket category not found."
#         )
    
#     # Validate dynamic fields against category field definitions
#     validation_errors = []
#     processed_dynamic_fields = {}
#     report_metadata = {}
    
#     for field_def in ticket_category.field_definitions:
#         field_name = field_def.name
#         field_value = data.dynamic_fields.get(field_name)
        
#         # Store field metadata for reporting
#         field_metadata = {
#             "label": field_def.label,
#             "type": field_def.type.value,
#             "value": field_value
#         }
        
#         # Validate required fields
#         if field_def.validation and field_def.validation.get("required", False):
#             if field_value is None or field_value == "":
#                 validation_errors.append(f"Field '{field_def.label}' is required.")
#                 continue
        
#         # Type validation
#         if field_value is not None:
#             if field_def.type == FieldType.NUMBER:
#                 try:
#                     field_value = float(field_value)
#                 except (ValueError, TypeError):
#                     validation_errors.append(f"Field '{field_def.label}' must be a number.")
#                     continue
#             elif field_def.type == FieldType.BOOLEAN:
#                 if not isinstance(field_value, bool):
#                     validation_errors.append(f"Field '{field_def.label}' must be a boolean.")
#                     continue
#             elif field_def.type == FieldType.SELECT:
#                 valid_options = [opt["value"] for opt in (field_def.options or [])]
#                 if field_value not in valid_options:
#                     validation_errors.append(f"Field '{field_def.label}' must be one of: {', '.join(valid_options)}")
#                     continue
        
#         # Store processed field
#         processed_dynamic_fields[field_name] = {
#             "value": field_value,
#             "label": field_def.label,
#             "type": field_def.type.value
#         }
        
#         # Add to report metadata if it's a report field
#         if field_def.is_report_field:
#             report_metadata[field_name] = {
#                 **field_metadata,
#                 "report_config": field_def.report_config
#             }
    
#     if validation_errors:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail={"message": "Validation errors", "errors": validation_errors}
#         )
    
#     # Create ticket with processed data
#     ticket_data = data.dict(exclude={'dynamic_fields'})
#     new_ticket = Ticket(**ticket_data)
#     new_ticket.dynamic_fields = processed_dynamic_fields
#     # Fix: Use report_data instead of report_metadata to match your DB model
#     new_ticket.report_data = report_metadata
    
#     db.add(new_ticket)
#     try:
#         db.commit()
#         db.refresh(new_ticket)
#     except IntegrityError as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An error occurred while creating the ticket. Please try again."
#         )

#     return {"message": "New ticket created", "new_ticket_id": new_ticket.id}





@app.post("/receive-data")
async def receive_json_data(data: Union[List[Dict[str, Any]], Dict[str, Any]]):
    """
    Receive JSON data and log it.
    
    Args:
        data: JSON data - can be a list of objects or a single object
    
    Returns:
        Success message with data info
    """
    try:
        # Print the received data to terminal
        print("=" * 50)
        print("RECEIVED JSON DATA:")
        print("=" * 50)
        print(json.dumps(data, indent=2))
        print("=" * 50)
        
        # Also log using logger
        logger.info("Received JSON data:")
        logger.info(json.dumps(data, indent=2))
        
        # Determine data type and structure
        if isinstance(data, list):
            data_type = "array"
            count = len(data)
            print(f"Data type: Array with {count} items")
            logger.info(f"Data type: Array with {count} items")
            
            # Log structure of first item if array is not empty
            if data and isinstance(data[0], dict):
                print(f"First item keys: {list(data[0].keys())}")
                logger.info(f"First item keys: {list(data[0].keys())}")
        elif isinstance(data, dict):
            data_type = "object"
            count = 1
            print(f"Data type: Single object")
            print(f"Object keys: {list(data.keys())}")
            logger.info(f"Data type: Single object")
            logger.info(f"Object keys: {list(data.keys())}")
        else:
            data_type = "unknown"
            count = 0
            print(f"Data type: {type(data)}")
            logger.info(f"Data type: {type(data)}")
        
        return {
            "message": "Data received and logged successfully",
            "data_type": data_type,
            "item_count": count,
            "status": "success",
            "received_data": data
        }
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")




@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
