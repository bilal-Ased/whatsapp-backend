from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from typing import List, Optional
from database import SessionLocal
from models import Customer  
from schemas.customer import CustomerModel
from sqlalchemy import func



router = APIRouter(
    tags=["customers"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@router.post("/create-customer")
def create_customer(data: CustomerModel, db: Session = Depends(get_db)):
    new_customer = Customer(**data.dict(exclude_unset=True, exclude={'id', 'created_at', 'updated_at'}))
    db.add(new_customer)
    try:
        db.commit()
        db.refresh(new_customer)
    except IntegrityError as e:
        db.rollback()
        error_message = str(e.orig)
        if isinstance(e.orig, Exception):
            if "unique constraint" in error_message.lower() or "duplicate entry" in error_message.lower():
                if "name" in error_message.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Name already exists. Please use a different name."
                    )
                elif "mobile_number" in error_message.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Mobile number already exists. Please use a different mobile number."
                    )
                elif "id_number" in error_message.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="ID number already exists. Please use a different ID number."
                    )
                elif "account_number" in error_message.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Account number already exists. Please use a different account number."
                    )
                elif "email_address" in error_message.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email address already exists. Please use a different email address."
                    )
            else:
                # Generic error for other integrity issues
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while creating the customer. Please try again."
                )

    return {"message": "New customer created", "new_customer_id": new_customer.id}

@router.get("/customers-list", response_model=List[CustomerModel])
def get_customers(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name, email, mobile")
):
    query = db.query(Customer)
    
    if search:
        search_term = f"%{search}%"
        full_name = func.concat(Customer.first_name, ' ', Customer.last_name)
        
        query = query.filter(
            or_(
                Customer.first_name.ilike(search_term),
                Customer.last_name.ilike(search_term),
                full_name.ilike(search_term),
                Customer.mobile_number.ilike(search_term),
                Customer.alternative_mobile_number.ilike(search_term),
                Customer.email_address.ilike(search_term)
            )
        )
    
    customers = query.all()
    
    # Convert to dict and add full_name manually
    result = []
    for customer in customers:
        customer_dict = {
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "mobile_number": customer.mobile_number,
            "email_address": customer.email_address,
            "alternative_mobile_number": customer.alternative_mobile_number,
            "created_at": customer.created_at,
            "updated_at": customer.updated_at,
            "full_name": f"{customer.first_name} {customer.last_name}" 
        }
        result.append(customer_dict)
    
    return result

@router.get("/{customer_id}", response_model=CustomerModel)
def get_customer_by_id(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific customer by ID
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=404, 
            detail=f"Customer with ID {customer_id} not found"
        )
    
    return customer