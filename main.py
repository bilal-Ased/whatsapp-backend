from fastapi import FastAPI, Depends, Query
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import CustomersTable,Tickets,TicketTypes,TicketPriority,ProductTypes,ResolutionTypes,Tenants,Properties
from models import MobileBankingData,CreditCardData
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import joinedload
from fastapi.middleware.cors import CORSMiddleware
from schemas.customer import CustomerCreate, CustomerUpdate,TicketCreate,TicketType,TicketStatus,ProductTypeModel,ResolutionTypeModel,TenantModel,PropertyModel
from schemas.customer import MobileCustomerData,CreditCardCustomerData
from sqlalchemy.exc import IntegrityError
from typing import Optional,List
from sqlalchemy import or_





app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you can specify your frontend domain like 
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)
# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/customers/list")
def webhook_get_all_customers(
    search: Optional[str] = Query(None, description="Search by name, phone, or ID"),
    db: Session = Depends(get_db)
):
    query = db.query(CustomersTable).options(
        joinedload(CustomersTable.mobile_banking_data),
        joinedload(CustomersTable.credit_card_data),
    )

    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(
            CustomersTable.first_name.ilike(search_term) |
            CustomersTable.middle_name.ilike(search_term) |
            CustomersTable.last_name.ilike(search_term) |
            CustomersTable.mobile_number.ilike(search_term) |
            CustomersTable.alternate_phone_number.ilike(search_term) |
            CustomersTable.identification_no.ilike(search_term) |
            CustomersTable.account_number.ilike(search_term)
        )

    customers = query.all()

    customer_list = []
    for customer in customers:
        customer_dict = {
            "Name": f"{customer.first_name} {customer.middle_name} {customer.last_name}",
            "Phone": customer.mobile_number,
            "Alternate Phone": customer.alternate_phone_number,
            "Id Number": customer.identification_no,
            "Account No": customer.account_number,
            "Email": customer.email,
            "Mobile Banking": "Yes" if customer.mobile_banking_data else "No",
            "Age": customer.age,
            "Gender": customer.gender,
            "Created At": str(customer.date_of_birth),
            "Status": customer.status
        }
        customer_list.append(customer_dict)

    return jsonable_encoder(customer_list)


@app.get("/get-mobile-banking-customers", response_model=list[MobileCustomerData])
def get_all_mobile_banking_customers(db:Session = Depends(get_db)):
    return db.query(MobileBankingData).all()

@app.get("/credit-card-customers", response_model=list[CreditCardCustomerData])
def get_all_credit_card_customers(db:Session = Depends(get_db)):
    return db.query(CreditCardData).all()

@app.post("/customers/create")
def create_customer(data: CustomerUpdate, db: Session = Depends(get_db)):
    new_customer = CustomersTable(**data.dict())

    db.add(new_customer)
    try:
        db.commit()
        db.refresh(new_customer)
    except IntegrityError as e:
        db.rollback()
        if "Duplicate entry" in str(e.orig):
            raise HTTPException(status_code=400, detail="Mobile number or ID number already exists.")
        raise HTTPException(status_code=500, detail="Database error.")

    return {"message": "Customer created", "customer_id": new_customer.id}



@app.put("/customers/update/{customer_id}")
def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    customer = db.query(CustomersTable).filter(CustomersTable.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found.")

    # Update fields dynamically from the request data
    for key, value in data.dict(exclude_unset=True).items():
        setattr(customer, key, value)

    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError as e:
        db.rollback()
        if "Duplicate entry" in str(e.orig):
            raise HTTPException(status_code=400, detail="Mobile number or ID number already exists.")
        raise HTTPException(status_code=500, detail="Database error during update.")

    return {"message": "Customer updated", "customer_id": customer.id}


@app.post("/ticket-type/create")
def create_ticket(data: TicketType, db: Session = Depends(get_db)):
    new_ticket_type = TicketTypes(**data.dict(exclude_unset=True))
    new_ticket_type = TicketTypes(**data.dict(exclude_unset=True))

    db.add(new_ticket_type)
    try:
        db.commit()
        db.refresh(new_ticket_type)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating ticket")

    return {"message": "Ticket type created", "ticket_id": new_ticket_type.id}


@app.post("/ticket-status/create")
def create_ticket_status(data: TicketStatus, db: Session = Depends(get_db)):
    new_ticket_status = TicketPriority(**data.dict(exclude_unset=True))
    db.add(new_ticket_status)
    try:
        db.commit()
        db.refresh(new_ticket_status)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating ticket")

    return {"message": "Ticket Status created", "ticket_status_id": new_ticket_status.id}


@app.post("/product-type/create")
def create_ticket_status(data: ProductTypeModel, db: Session = Depends(get_db)):
    new_product_type = ProductTypes(**data.dict(exclude_unset=True))
    db.add(new_product_type)
    try:
        db.commit()
        db.refresh(new_product_type)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating ticket")

    return {"message": "Product Type created", "ticket_status_id": new_product_type.id}


@app.post("/resolution-type/create")
def create_resolution_type(data: ResolutionTypeModel, db: Session = Depends(get_db)):
    new_resolution_type = ResolutionTypes(**data.dict(exclude_unset=True))
    db.add(new_resolution_type)
    try:
        db.commit()
        db.refresh(new_resolution_type)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating resolution type")

    return {"message": "Resolution Type created", "resolution_type_id": new_resolution_type.id}



@app.post("/tickets/create")
def create_ticket(data: TicketCreate, db: Session = Depends(get_db)):
    new_ticket = Tickets(**data.dict())

    db.add(new_ticket)
    try:
        db.commit()
        db.refresh(new_ticket)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating ticket")

    return {"message": "Ticket created", "ticket_id": new_ticket.id}




# property management code

@app.post("/create-tenant")
def create_tenant(data: TenantModel, db: Session = Depends(get_db)):
    new_tenant = Tenants(**data.dict(exclude_unset=True))
    db.add(new_tenant)
    try:
        db.commit()
        db.refresh(new_tenant)
    except IntegrityError as e:
        db.rollback()
        error_message = str(e.orig)
        if isinstance(e.orig, Exception):
            if "unique constraint" in error_message.lower() or "duplicate entry" in error_message.lower():
                if "email" in error_message.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already exists. Please use a different email."
                    )
                elif "phone" in error_message.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Phone number already exists. Please use a different phone number."
                    )
            else:
                # Generic error for other integrity issues
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="An error occurred while creating the tenant. Please try again."
                )

    return {"message": "New tenant created", "new_tenant_id": new_tenant.id}


@app.get("/tenants-list", response_model=List[TenantModel])
def get_tenants(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or email")
):
    """
    Get list of tenants with optional search
    """
    query = db.query(Tenants)
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Tenants.first_name.ilike(search_term),
                Tenants.last_name.ilike(search_term),
                Tenants.email.ilike(search_term),
                Tenants.phone.ilike(search_term),
                Tenants.lease_end_date.ilike(search_term),
                Tenants.move_in_date.ilike(search_term),
            )
        )
    
    tenants = query.all()
    return tenants


@app.post("/create-property")
def create_property(data: PropertyModel, db: Session = Depends(get_db)):
    new_property = Properties(**data.dict())
    db.add(new_property)
    try:
        db.commit()
        db.refresh(new_property)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating property")

    return {"message": "Property created", "new_property": new_property.property_name}


@app.get("/properties-list", response_model=List[PropertyModel])
def get_properties(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name")
):
    """
    Get list of tenants with optional search
    """
    query = db.query(Properties)
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Properties.property_name.ilike(search_term),
                Properties.address.ilike(search_term),
                Properties.unit_number.ilike(search_term),
                Properties.bedrooms.ilike(search_term),
                Properties.monthly_rent.ilike(search_term),
            )
        )
    
    properties = query.all()
    return properties



@app.get("/total-count")
def get_total_count(type: str = Query(..., description="Type can be 'tenants' or 'properties'"), db: Session = Depends(get_db)):
    if type == "properties":
        count = db.query(Properties).count()
    elif type == "tenants":
        count = db.query(Tenants).count()
    else:
        raise HTTPException(status_code=400, detail="Invalid type. Use 'tenants' or 'properties'.")
    
    return {"type": type, "total_count": count}