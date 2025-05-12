from fastapi import FastAPI, Depends, Query,Request
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import CustomersTable,Tickets,TicketTypes,TicketPriority,ProductTypes,ResolutionTypes,Tenants,Properties,User,Leases
from models import MobileBankingData,CreditCardData
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import joinedload
from fastapi.middleware.cors import CORSMiddleware
from schemas.customer import CustomerCreate, CustomerUpdate,TicketCreate,TicketType,TicketStatus,ProductTypeModel,ResolutionTypeModel,TenantModel,PropertyModel,UserCreate,UserLogin,LeaseBase,LeaseWithDetails
from schemas.customer import MobileCustomerData,CreditCardCustomerData
from sqlalchemy.exc import IntegrityError
from typing import Optional,List
from sqlalchemy import or_
from security import get_password_hash
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import desc

from utils import get_current_user
from typing import List, Dict, Any



app = FastAPI()


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




@app.get("/leases-list", response_model=List[LeaseWithDetails])
def get_leases(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or email")
):
    query = db.query(
        Leases.id,
        Leases.start_date,
        Leases.end_date,
        Leases.monthly_rent,
        Leases.deposit,
        Leases.lease_document,
        Leases.status,
        (Tenants.first_name + ' ' + Tenants.last_name).label("tenant_name"),
        Tenants.phone.label("tenant_phone"),
        Tenants.email.label("tenant_email"),
        Properties.property_name.label("property_name")
    ).join(
        Tenants, Leases.tenant_id == Tenants.id
    ).join(
        Properties, Leases.property_id == Properties.id
    )
    
    if search:
        query = query.filter(
            or_(
                (Tenants.first_name + ' ' + Tenants.last_name).ilike(f"%{search}%"),
                Properties.property_name.ilike(f"%{search}%")
            )
        )
    
    result = query.all()
    
    if result:
        print("First row attributes:", dir(result[0]))
        print("First row as dict:", result[0]._asdict())
    else:
        leases_list = [LeaseWithDetails(
        id=row.id,
        start_date=row.start_date,
        end_date=row.end_date,
        monthly_rent=row.monthly_rent,
        deposit=row.deposit,
        lease_document=row.lease_document,
        status=row.status,
        tenant_name=row.tenant_name,
        tenant_phone=row.tenant_phone,
        tenant_email=row.tenant_email,
        property_name=row.property_name,
    ) for row in result]

    return leases_list


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


@app.post("/create-lease")
def create_lease(data: LeaseBase, db: Session = Depends(get_db)):
    new_lease = Leases(**data.dict())
    db.add(new_lease)
    try:
        db.commit()
        db.refresh(new_lease)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error creating lease")

    return {
        "message": "Lease created",
        "lease_id": new_lease.id
    }





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
    elif type == "users":
        count = db.query(User).count()
    elif type == "leases":
        count = db.query(Leases).count()
        
    else:
        raise HTTPException(status_code=400, detail="Invalid type. Use 'tenants' or 'properties'.")
    
    return {"type": type, "total_count": count}



@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user.username) |
        (User.email == user.email) |
        (User.phone == user.phone)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash password and create user
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        phone=user.phone,
        hashed_password=hashed_password,
  
    )
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}


# function for login for a user 


# Config
SECRET_KEY = "UTibWLh9hs"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 12 * 60  # 12 hours

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": db_user.email})
    
    return {
        "message": "Login successful!",
        "access_token": access_token,
        "token_type": "bearer"
    }




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "phone": current_user.phone,
    }

@app.get("/users-list", response_model=List[UserCreate])
def get_users(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or Email")
):
    """
    Get list of users with optional search
    """
    query = db.query(User)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term),
                User.phone.ilike(search_term),
               
            )
        )
    
    users = query.all()
    return users



@app.get("/tenants-last-five", response_model=List[TenantModel])
def get_tenants(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or email")
):
    """
    Get list of tenants with optional search
    """
    query = db.query(Tenants)
   
    
    tenants = query.order_by(desc(Tenants.created_at)).limit(5).all()
    return tenants




@app.get("/global-search")
def global_search(
    search: str = Query(..., min_length=1, description="Search across tenants, properties, leases, and users"),
    db: Session = Depends(get_db)
) -> Dict[str, List[Dict[str, Any]]]:
    search_term = f"%{search}%"

    # Tenants search
    tenants_query = db.query(Tenants).filter(
        or_(
            Tenants.first_name.ilike(search_term),
            Tenants.last_name.ilike(search_term),
            Tenants.email.ilike(search_term),
            Tenants.phone.ilike(search_term),
        )
    )
    tenants = [
        {
            "type": "tenant",
            "id": t.id,
            "name": f"{t.first_name} {t.last_name}",
            "email": t.email,
            "phone": t.phone,
        } for t in tenants_query.all()
    ]

    # Properties search
    properties_query = db.query(Properties).filter(
        or_(
            Properties.property_name.ilike(search_term),
            Properties.address.ilike(search_term),
            Properties.unit_number.ilike(search_term),
        )
    )
    properties = [
        {
            "type": "property",
            "id": p.id,
            "property_name": p.property_name,
            "address": p.address,
            "unit_number": p.unit_number,
        } for p in properties_query.all()
    ]

    # Leases search
    leases_query = db.query(Leases).filter(
        or_(
            Leases.status.ilike(search_term),
            Leases.lease_document.ilike(search_term)
        )
    )
    leases = [
        {
            "type": "lease",
            "id": l.id,
            "tenant_id": l.tenant_id,
            "property_id": l.property_id,
            "status": l.status,
        } for l in leases_query.all()
    ]

    return {
        "tenants": tenants,
        "properties": properties,
        "leases": leases,
    }


# get tenant info 

@app.get("/tenant/{tenant_id}/profile", response_model=List[LeaseWithDetails])
def get_tenant_leases(
    tenant_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all leases associated with a specific tenant ID
    """
    query = db.query(
        Leases.id,
        Leases.start_date,
        Leases.end_date,
        Leases.monthly_rent,
        Leases.deposit,
        Leases.lease_document,
        Leases.status,
        (Tenants.first_name + ' ' + Tenants.last_name).label("tenant_name"),
         Tenants.phone.label("tenant_phone"),
        Properties.property_name.label("property_name")
    ).join(
        Tenants, Leases.tenant_id == Tenants.id
    ).join(
        Properties, Leases.property_id == Properties.id
    ).filter(
        Tenants.id == tenant_id
    )
    
    result = query.all()

    # Check if any leases were found for the tenant
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"No leases found for tenant with ID {tenant_id}"
        )

    # Format the result into Pydantic models
    leases_list = [LeaseWithDetails(
        id=row.id,
        start_date=row.start_date,
        end_date=row.end_date,
        monthly_rent=row.monthly_rent,
        deposit=row.deposit,
        lease_document=row.lease_document,
        status=row.status,
        tenant_name=row.tenant_name,
        tenant_phone=row.tenant_phone,
        property_name=row.property_name,
    ) for row in result]
    
    print('hello bilal')

    return leases_list


@app.post("/tickets-data")
async def tickets_data(request:Request):
    data = await request.json()
    customer_name = data.get(customer_name,"").strip()
    customer_phone = data.get(customer_phone,"")
    created_by = data.get(created_by,"")
    location = data.get(location,"").strip()
    customer_email = data.get("customer_email", "")
    ticket_status = data.get("status", "")
    date_created = data.get("date_created")
    
    try:
        created_at = datetime.fromtimestamp(int(date_created) / 1000).strftime('%Y-%m-%d %H:%M:%S')
    except:
        created_at = None

    transformed = {
        "name": customer_name,
        "number": f"+{customer_phone}" if customer_phone else None,
        "created_by": created_by,
        "created_at": created_at,
        "location": location,
        "customer_email": customer_email,
        "ticket_status": ticket_status
    }

    return transformed
    
    


    
