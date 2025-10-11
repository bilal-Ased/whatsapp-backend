from fastapi import FastAPI, Depends, Query,Request
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Tenants,Properties,User,Leases,Email,EmailAttachment,EmailParticipant,Payments,PaymentSchedule
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import joinedload
from fastapi.middleware.cors import CORSMiddleware
from schemas.customer import TenantModel,PropertyModel,UserCreate,UserLogin,LeaseBase,LeaseWithDetails,EmailRead,PaymentCreate,UserRead
from sqlalchemy.exc import IntegrityError
from typing import Optional,List
from sqlalchemy import func, and_, or_
from security import get_password_hash
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import desc
from sqlalchemy.exc import NoResultFound
from utils import get_current_user
from typing import List, Dict, Any
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
from services.whatsapp import send_payment_confirmation
import calendar
from sqlalchemy import or_, and_
from fastapi.responses import StreamingResponse
from generate_invoice.invoice import generate_invoice
import logging
from sqlalchemy import or_, cast, String
from sqlalchemy import func, select


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://silver-fox-mgt.web.app",
        "https://silver-fox-mgt.web.app/signin",  # Add this if needed
    ],
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
        
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)






app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")





@app.post("/create-tenant")
def create_tenant(data: TenantModel, db: Session = Depends(get_db)):
    # Exclude auto-generated fields (id, created_at, updated_at are handled by DB)
    new_tenant = Tenants(**data.dict(exclude_unset=True, exclude={'id', 'created_at', 'updated_at'}))
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




@app.put("/update-tenant/{tenant_id}")
def update_tenant(tenant_id: int, data: TenantModel, db: Session = Depends(get_db)):
    # Check if tenant exists
    tenant = db.query(Tenants).filter(Tenants.id == tenant_id).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with ID {tenant_id} not found."
        )
    
    # Update tenant fields with provided data
    update_data = data.dict(exclude_unset=True, exclude={'id', 'created_at', 'updated_at'})
    
    for key, value in update_data.items():
        setattr(tenant, key, value)
    
    try:
        db.commit()
        db.refresh(tenant)
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
                    detail="An error occurred while updating the tenant. Please try again."
                )
    
    return {
        "message": "Tenant updated successfully",
        "tenant_id": tenant.id,
        "updated_data": {
            "first_name": tenant.first_name,
            "last_name": tenant.last_name,
            "email": tenant.email,
            "phone": tenant.phone,
            "emergency_contact": tenant.emergency_contact
        }
    }
    
@app.get("/tenants-list")
def get_tenants(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name or email"),
    available_only: bool = Query(False, description="Show only tenants without active lease")
):
    query = db.query(
        Tenants.id,
        Tenants.first_name,
        Tenants.last_name,
        Tenants.email,
        Tenants.phone,
        Tenants.emergency_contact,
        Tenants.active_status,
        Tenants.created_at,
        Tenants.updated_at,
        Leases.id.label('lease_id'),
        Leases.start_date.label('move_in_date'),
        Leases.end_date.label('lease_end_date')
    ).outerjoin(
        Leases, 
        and_(
            Leases.tenant_id == Tenants.id,
            Leases.status == "active"
        )
    )

    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Tenants.first_name.ilike(search_term),
                Tenants.last_name.ilike(search_term),
                Tenants.email.ilike(search_term),
                Tenants.phone.ilike(search_term)
            )
        )

    # Filter only tenants without active lease
    if available_only:
        query = query.filter(Leases.id == None)

    # Order by most recent tenant
    query = query.order_by(Tenants.created_at.desc())

    results = query.all()

    tenants = []
    for row in results:
        tenants.append({
            "id": row.id,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "email": row.email,
            "phone": row.phone,
            "emergency_contact": row.emergency_contact,
            "active_status": row.active_status,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
            "lease_id": row.lease_id,
            "move_in_date": row.move_in_date,
            "lease_end_date": row.lease_end_date
        })

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
        Leases.tenant_id,
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
    
    leases_list = [] 
    
    if result:
        leases_list = [
            LeaseWithDetails(
                id=row.id,
                start_date=row.start_date,
                end_date=row.end_date,
                monthly_rent=row.monthly_rent,
                deposit=row.deposit,
                lease_document=row.lease_document,
                status=row.status,
                tenant_id=row.tenant_id,
                tenant_name=row.tenant_name,
                tenant_phone=row.tenant_phone,
                tenant_email=row.tenant_email,
                property_name=row.property_name,
            )
            for row in result
        ]

    return leases_list



@app.post("/create-property")
def create_property(data: PropertyModel, db: Session = Depends(get_db)):
    STATUS_MAPPING = {
        "Vacant": 0,
        "Booked": 1
    }

    # 🔍 Pre-check if unit_number already exists
    existing = db.query(Properties).filter(Properties.unit_number == data.unit_number).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Unit number '{data.unit_number}' already exists"
        )

    # Default to 0 if not provided or invalid
    status_value = STATUS_MAPPING.get(data.status, 0)

    new_property = Properties(
        property_name=data.property_name,
        address=data.address,
        unit_number=data.unit_number,
        bedrooms=data.bedrooms,
        status=status_value,
        monthly_rent=data.monthly_rent,
        created_at=data.created_at,
        updated_at=data.updated_at
    )

    db.add(new_property)
    db.commit()
    db.refresh(new_property)

    return {
        "message": "Property created",
        "new_property": new_property.property_name,
        "status": "Vacant" if status_value == 0 else "Booked"
    }



@app.put("/update-property/{property_id}")
def update_property(property_id: int, data: PropertyModel, db: Session = Depends(get_db)):
    STATUS_MAPPING = {
        "Vacant": 0,
        "Booked": 1
    }

    # 🔍 Check if property exists
    existing_property = db.query(Properties).filter(Properties.id == property_id).first()
    if not existing_property:
        raise HTTPException(
            status_code=404,
            detail=f"Property with ID {property_id} not found"
        )

    # 🔍 Check if unit_number is being changed and if it already exists (excluding current property)
    if data.unit_number != existing_property.unit_number:
        duplicate_unit = db.query(Properties).filter(
            Properties.unit_number == data.unit_number,
            Properties.id != property_id
        ).first()
        if duplicate_unit:
            raise HTTPException(
                status_code=400,
                detail=f"Unit number '{data.unit_number}' already exists"
            )

    # Map status to integer value, default to current status if not provided or invalid
    status_value = STATUS_MAPPING.get(data.status, existing_property.status)

    # Update property fields
    existing_property.property_name = data.property_name
    existing_property.address = data.address
    existing_property.unit_number = data.unit_number
    existing_property.bedrooms = data.bedrooms
    existing_property.status = status_value
    existing_property.monthly_rent = data.monthly_rent
    existing_property.updated_at = datetime.utcnow()  # Auto-update timestamp

    db.commit()
    db.refresh(existing_property)

    return {
        "message": "Property updated successfully",
        "id": existing_property.id,
        "property_name": existing_property.property_name,
        "address": existing_property.address,
        "unit_number": existing_property.unit_number,
        "bedrooms": existing_property.bedrooms,
        "monthly_rent": str(existing_property.monthly_rent),
        "status": "Vacant" if status_value == 0 else "Booked",
        "updated_at": existing_property.updated_at.isoformat() if existing_property.updated_at else None
    }

@app.post("/create-lease")
def create_lease(
    tenant_id: int = Form(...),
    property_id: int = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    monthly_rent: Decimal = Form(...),
    deposit: Decimal = Form(...),
    status: str = Form("active"),
    lease_document: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    file_path = None
    if lease_document:
        # Ensure uploads directory exists
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # Generate unique filename to avoid overwrites
        extension = lease_document.filename.split('.')[-1]
        unique_name = f"{uuid4().hex}.{extension}"
        file_path = os.path.join(upload_dir, unique_name)

        # Save the file
        with open(file_path, "wb") as f:
            f.write(lease_document.file.read())

    new_lease = Leases(
        tenant_id=tenant_id,
        property_id=property_id,
        start_date=start_date,
        end_date=end_date,
        monthly_rent=monthly_rent,
        deposit=deposit,
        status=status,
        lease_document=file_path
    )

    db.add(new_lease)
    try:
        db.commit()
        db.refresh(new_lease)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating lease: {str(e)}")

    return {"message": "Lease created", "lease_id": new_lease.id}


@app.get("/vacant-properties", response_model=List[PropertyModel])
def get_vacant_properties(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name"),
):
 
    query = db.query(Properties).options(joinedload(Properties.leases))

    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Properties.property_name.ilike(search_term),
                Properties.address.ilike(search_term),
                Properties.unit_number.ilike(search_term),
            )
        )

    # Only properties with no leases
    properties = [p for p in query.all() if not p.leases]

    result = []
    for prop in properties:
        result.append(
            PropertyModel(
                id=prop.id,
                property_name=prop.property_name,
                address=prop.address,
                unit_number=prop.unit_number,
                bedrooms=prop.bedrooms,
                monthly_rent=prop.monthly_rent,
                status="Vacant",
                created_at=prop.created_at,
                updated_at=prop.updated_at,
            )
        )

    return result



@app.get("/properties-list", response_model=List[PropertyModel])
def get_properties(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by name"),
):
    """
    Get list of properties with status (Booked/Vacant)
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
            )
        )

    properties = query.all()

    result = []
    for prop in properties:
        has_tenant = bool(prop.leases)
        status = "Booked" if has_tenant else "Vacant"

        result.append(
            PropertyModel(
                id=prop.id,
                property_name=prop.property_name,
                address=prop.address,
                unit_number=prop.unit_number,
                bedrooms=prop.bedrooms,
                monthly_rent=prop.monthly_rent,
                status=status,
                created_at=prop.created_at,
                updated_at=prop.updated_at,
            )
        )

    return result


@app.get("/total-count")
def get_total_count(
    type: str = Query(..., description="Type can be 'tenants', 'properties', 'users', or 'leases'"),
    db: Session = Depends(get_db)
):
    model_map = {
        "properties": Properties,
        "tenants": Tenants,
        "users": User,
        "leases": Leases,
        "payments": Payments
    }

    model = model_map.get(type)
    if not model:
        raise HTTPException(status_code=400, detail="Invalid type.")

    # Use SQLAlchemy Core for efficiency
    stmt = select(func.count()).select_from(model.__table__)
    count = db.execute(stmt).scalar()

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
        status=user.status,
        created_at=user.created_at or datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "id": new_user.id}


@app.get("/payments-list")
def get_payments(
    tenant_id: Optional[int] = Query(None, description="Filter by tenant ID"),
    lease_id: Optional[int] = Query(None, description="Filter by lease ID"),
    db: Session = Depends(get_db)
):
    query = db.query(Payments).join(Payments.tenant).join(Payments.lease)

    # Apply filters
    if tenant_id:
        query = query.filter(Payments.tenant_id == tenant_id)
    if lease_id:
        query = query.filter(Payments.lease_id == lease_id)

    payments = query.all()
    if not payments:
        raise HTTPException(status_code=404, detail="No payments found")

    result = []
    for p in payments:
        result.append({
            "payment_id": p.id,
            "tenant_id": p.tenant_id,
            "tenant_name": f"{p.tenant.first_name} {p.tenant.last_name}",
            "lease_id": p.lease_id,
            "property": p.lease.property.property_name,
            "unit_number": p.lease.property.unit_number,
            "amount": str(p.amount),
            "payment_date": p.payment_date.strftime("%Y-%m-%d"),
            "payment_method": p.payment_method,
            "payment_status": p.payment_status,
            "transaction_reference": p.transaction_reference,
            "late_fee": str(p.late_fee),
            "notes": p.notes,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": p.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return {"count": len(result), "payments": result}


# Config
SECRET_KEY = "UTibWLh9hs"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 12 * 60  # 12 hours

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    # Truncate to 72 bytes (not characters) for bcrypt
    password_bytes = password.encode('utf-8')[:72]
    password = password_bytes.decode('utf-8', errors='ignore')
    print(f"[HASH] Password length: {len(password)} chars, {len(password.encode('utf-8'))} bytes")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate to 72 bytes (not characters) for bcrypt
    password_bytes = plain_password.encode('utf-8')[:72]
    plain_password = password_bytes.decode('utf-8', errors='ignore')
    print(f"[VERIFY] Password length: {len(plain_password)} chars, {len(plain_password.encode('utf-8'))} bytes")
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    try:
        print(f"[LOGIN] Attempting login for email: {user.email}")
        print(f"[LOGIN] Password length received: {len(user.password)} chars, {len(user.password.encode('utf-8'))} bytes")
        
        # Check if user exists
        db_user = db.query(User).filter(User.email == user.email).first()
        
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        print(f"[LOGIN] User found in database")
        
        if not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        access_token = create_access_token(data={"sub": db_user.email})
        
        return {
            "message": "Login successful!",
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "phone": current_user.phone,
    }

@app.get("/users-list", response_model=List[UserRead])
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

    # --- Tenants search ---
    tenants_query = db.query(Tenants).filter(
        or_(
            cast(Tenants.first_name, String).ilike(search_term),
            cast(Tenants.last_name, String).ilike(search_term),
            cast(Tenants.email, String).ilike(search_term),
            cast(Tenants.phone, String).ilike(search_term),
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

    # --- Properties search ---
    properties_query = db.query(Properties).filter(
        or_(
            cast(Properties.property_name, String).ilike(search_term),
            cast(Properties.address, String).ilike(search_term),
            cast(Properties.unit_number, String).ilike(search_term),
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

    # --- Leases search (fixed with casting) ---
    leases_query = db.query(Leases).filter(
        or_(
            cast(Leases.status, String).ilike(search_term),
            cast(Leases.lease_document, String).ilike(search_term),
        )
    )
    leases = [
        {
            "type": "lease",
            "id": l.id,
            "tenant_id": l.tenant_id,
            "property_id": l.property_id,
            "status": str(l.status),
            "lease_document": str(l.lease_document),
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
        Tenants.id.label("tenant_id"),  # Changed from Tenants.tenant_id to Tenants.id
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
        tenant_id=row.tenant_id,
        tenant_name=row.tenant_name,
        tenant_phone=row.tenant_phone,
        property_name=row.property_name,
    ) for row in result]
    
    return leases_list

@app.post("/tickets-data")
async def tickets_data(request:Request):
    data = await request.json()
    customer_name = data.get("customer_name", "").strip()
    customer_phone = data.get("customer_phone","")
    created_by = data.get("created_by","")
    location = data.get("location","").strip()
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
    
    

NYLAS_GRANT_ID = "e0722923-ae09-4f36-8a04-f85bed5c7ddd"
NYLAS_API_URL = f"https://api.eu.nylas.com/v3/grants/{NYLAS_GRANT_ID}/messages/send"
NYLAS_API_TOKEN = "nyk_v0_H3dZasch36zm9XpLwMQ2eOEqcdvTyUdCpXA7s6NSiq3E5iLPtD6XHISwpOridt61"




    
class Recipient(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class TrackingOptions(BaseModel):
    opens: Optional[bool] = None
    links: Optional[bool] = None
    thread_replies: Optional[bool] = None
    label: Optional[str] = None

class Attachment(BaseModel):
    filename: str
    content: str  # base64 encoded
    content_type: str
    

class EmailRequest(BaseModel):
    subject: str
    to: List[Recipient]
    cc: Optional[List[Recipient]] = None
    bcc: Optional[List[Recipient]] = None
    reply_to: Optional[List[Recipient]] = None
    body: str
    tracking_options: Optional[TrackingOptions] = None
    attachments: Optional[List[Attachment]] = None




    
@app.post("/send-email")
async def send_email(request: EmailRequest):
    headers = {
        "Authorization": f"Bearer {NYLAS_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = request.dict(exclude_none=True)

    async with httpx.AsyncClient() as client:
        response = await client.post(NYLAS_API_URL, json=payload, headers=headers)

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Failed to send email: {response.text}"
        )

    return {
        "message": "Email sent successfully",
        "response": response.json()
    }



@app.post("/email-webhook", status_code=status.HTTP_200_OK)
async def nylas_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()

    if payload.get("object") == "message" and payload.get("type") == "message.created":
        data = payload.get("data", {})

        email_id = data.get("id")
        thread_id = data.get("thread_id")
        grant_id = data.get("grant_id")
        subject = data.get("subject")
        snippet = data.get("snippet")
        date = datetime.fromtimestamp(data.get("date") / 1000) if data.get("date") else None
        folder = data.get("folder", {}).get("display_name", "INBOX")
        unread = data.get("unread", False)
        starred = data.get("starred", False)
        has_attachments = data.get("has_attachments", False)
        attachment_count = len(data.get("files", []))

        email = Email(
            id=email_id,
            thread_id=thread_id,
            grant_id=grant_id,
            subject=subject,
            snippet=snippet,
            date=date,
            folder=folder,
            unread=unread,
            starred=starred,
            has_attachments=has_attachments,
            attachment_count=attachment_count
        )
        db.add(email)

        # Participants
        for ptype in ["from", "to", "cc", "bcc", "reply_to"]:
            for p in data.get(ptype, []):
                participant = EmailParticipant(
                    email_id=email_id,
                    participant_type=ptype,
                    email_address=p.get("email"),
                    display_name=p.get("name")
                )
                db.add(participant)

        # Attachments
        for file in data.get("files", []):
            attachment = EmailAttachment(
                id=file["id"],
                email_id=email_id,
                filename=file.get("filename"),
                content_type=file.get("content_type"),
                size=file.get("size"),
                is_inline=file.get("is_inline", False)
            )
            db.add(attachment)

        db.commit()

    return JSONResponse(content={"status": "ok"})



@app.get("/emails", response_model=List[EmailRead])
def get_emails(db: Session = Depends(get_db)):
    emails = db.query(Email).options(
        joinedload(Email.attachments),
        joinedload(Email.participants)
    ).all()
    return emails


@app.get("/export")
def export_csv(
    table: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db)
):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in YYYY-MM-DD format")

    # Basic table name check (optional but recommended)
    if ";" in table or "--" in table:
        raise HTTPException(status_code=400, detail="Invalid table name")

    # Raw SQL query
    query = text(f"SELECT * FROM {table} WHERE created_at BETWEEN :start AND :end")
    result = db.execute(query, {"start": start, "end": end})
    rows = result.fetchall()
    headers = result.keys()

    # Write to CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    output.seek(0)

    filename = f"{table}_{start_date}_to_{end_date}.csv"
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )




# Main payments listing endpoint
@app.get("/payments-list")
def get_payments_list(
    search: Optional[str] = Query(None, description="Search by tenant name, property name, or transaction reference"),
    db: Session = Depends(get_db)
):
    """
    Get list of all payments with tenant and property information
    Supports search functionality for tenant name, property name, and transaction reference
    """
    try:
        # Base query with joins to get tenant and property information
        query = db.query(
            Payments.id,
            Payments.tenant_id,
            Payments.lease_id,
            Payments.payment_date,
            Payments.amount,
            Payments.payment_method,
            Payments.payment_status,
            Payments.transaction_reference,
            Payments.notes,
            Payments.created_at,
            # Tenant information
            (Tenants.first_name + ' ' + Tenants.last_name).label('tenant_name'),
            Tenants.first_name,
            Tenants.last_name,
            Tenants.email.label('tenant_email'),
            Tenants.phone.label('tenant_phone'),
            # Property information from lease
            Properties.name.label('property_name'),
            Properties.address.label('property_address'),
            # Lease information
            Leases.unit_number,
            Leases.rent_amount
        ).join(
            Tenants, Payments.tenant_id == Tenants.id
        ).join(
            Leases, Payments.lease_id == Leases.id
        ).join(
            Properties, Leases.property_id == Properties.id
        )

        # Apply search filter if provided
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    (Tenants.first_name + ' ' + Tenants.last_name).ilike(search_term),
                    Properties.name.ilike(search_term),
                    Payments.transaction_reference.ilike(search_term),
                    Tenants.email.ilike(search_term)
                )
            )

        # Order by payment date (most recent first)
        payments = query.order_by(Payments.payment_date.desc()).all()

        if not payments:
            return []

        # Format the response to match frontend expectations
        payments_list = []
        for payment in payments:
            payment_data = {
                "id": int(payment.id),
                "tenant_id": payment.tenant_id,
                "lease_id": payment.lease_id,
                "tenant_name": payment.tenant_name,
                "tenant_email": payment.tenant_email,
                "tenant_phone": payment.tenant_phone,
                "property_name": payment.property_name,
                "property_address": payment.property_address,
                "unit_number": payment.unit_number,
                "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
                "amount": str(payment.amount),  # Convert to string for frontend formatting
                "payment_method": payment.payment_method,
                "payment_status": payment.payment_status,
                "transaction_reference": payment.transaction_reference,
                "notes": payment.notes,
                "rent_amount": str(payment.rent_amount) if payment.rent_amount else None,
                "created_at": payment.created_at.isoformat() if payment.created_at else None
            }
            payments_list.append(payment_data)

        return payments_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching payments: {str(e)}")


@app.post("/payments/")
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    # Verify tenant exists
    tenant = db.query(Tenants).filter(Tenants.id == payment.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Verify lease exists
    lease = db.query(Leases).filter(Leases.id == payment.lease_id).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found")

    # Create payment
    new_payment = Payments(
        tenant_id=payment.tenant_id,
        lease_id=payment.lease_id,
        payment_date=date.today(),
        amount=payment.amount,
        payment_method=payment.payment_method,
        payment_status="pending",
        transaction_reference=payment.transaction_reference,
        notes=payment.notes
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return {
        "payment_id": new_payment.id,
        "tenant": f"{tenant.first_name} {tenant.last_name}",
        "lease_id": payment.lease_id,
        "amount": float(new_payment.amount),
        "status": new_payment.payment_status
    }


@app.put("/payments/{payment_id}/status")
async def update_payment_status(payment_id: int, status: str, db: Session = Depends(get_db)):
    try:
        payment = db.query(Payments).filter(Payments.id == payment_id).one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Payment not found")

    # update payment status
    payment.payment_status = status
    db.commit()
    db.refresh(payment)

    # fire WhatsApp only if completed
    if status == "completed":
        tenant = payment.tenant
        lease = payment.lease
        property_ = lease.property

        tenant_name = f"{tenant.first_name} {tenant.last_name}"
        tenant_phone = tenant.phone
        unit = f"Unit {property_.unit_number}" if property_.unit_number else property_.property_name
        invoice_number = payment.transaction_reference or f"PAY-{payment.id}"
        amount = f"${payment.amount}"
        month = calendar.month_name[payment.payment_date.month]
        payment_date = str(payment.payment_date)

        try:
            result = await send_payment_confirmation(
                to=tenant_phone,
                customer_name=tenant_name,
                amount=amount,
                month=month,
                invoice_number=invoice_number,
                payment_date=payment_date,
                unit=unit
            )
            return {
                "payment_id": payment.id,
                "status": "completed",
                "whatsapp_response": result
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Payment updated but WhatsApp failed: {str(e)}"
            )

    return {"payment_id": payment.id, "status": status}




# Main payments listing endpoint
@app.get("/payments-list")
def get_payments_list(
    search: Optional[str] = Query(None, description="Search by tenant name, property name, or transaction reference"),
    db: Session = Depends(get_db)
):
    """
    Get list of all payments with tenant and property information
    Supports search functionality for tenant name, property name, and transaction reference
    """
    try:
        # Base query with joins to get tenant and property information
        query = db.query(
            Payments.id,
            Payments.tenant_id,
            Payments.lease_id,
            Payments.payment_date,
            Payments.amount,
            Payments.payment_method,
            Payments.payment_status,
            Payments.transaction_reference,
            Payments.notes,
            Payments.created_at,
            # Tenant information
            (Tenants.first_name + ' ' + Tenants.last_name).label('tenant_name'),
            Tenants.first_name,
            Tenants.last_name,
            Tenants.email.label('tenant_email'),
            Tenants.phone.label('tenant_phone'),
            # Property information from lease
            Properties.name.label('property_name'),
            Properties.address.label('property_address'),
            # Lease information
            Leases.unit_number,
            Leases.rent_amount
        ).join(
            Tenants, Payments.tenant_id == Tenants.id
        ).join(
            Leases, Payments.lease_id == Leases.id
        ).join(
            Properties, Leases.property_id == Properties.id
        )

        # Apply search filter if provided
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    (Tenants.first_name + ' ' + Tenants.last_name).ilike(search_term),
                    Properties.name.ilike(search_term),
                    Payments.transaction_reference.ilike(search_term),
                    Tenants.email.ilike(search_term)
                )
            )

        # Order by payment date (most recent first)
        payments = query.order_by(Payments.payment_date.desc()).all()

        if not payments:
            return []

        # Format the response to match frontend expectations
        payments_list = []
        for payment in payments:
            payment_data = {
                "id": payment.id,
                "tenant_id": payment.tenant_id,
                "lease_id": payment.lease_id,
                "tenant_name": payment.tenant_name,
                "tenant_email": payment.tenant_email,
                "tenant_phone": payment.tenant_phone,
                "property_name": payment.property_name,
                "property_address": payment.property_address,
                "unit_number": payment.unit_number,
                "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
                "amount": str(payment.amount),  # Convert to string for frontend formatting
                "payment_method": payment.payment_method,
                "payment_status": payment.payment_status,
                "transaction_reference": payment.transaction_reference,
                "notes": payment.notes,
                "rent_amount": str(payment.rent_amount) if payment.rent_amount else None,
                "created_at": payment.created_at.isoformat() if payment.created_at else None
            }
            payments_list.append(payment_data)

        return payments_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching payments: {str(e)}")

# Payment creation endpoint (your existing one, enhanced)
@app.post("/payments/")
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    """
    Create a new payment record
    """
    # Verify tenant exists
    tenant = db.query(Tenants).filter(Tenants.id == payment.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Verify lease exists and belongs to the tenant
    lease = db.query(Leases).filter(
        Leases.id == payment.lease_id,
        Leases.tenant_id == payment.tenant_id
    ).first()
    if not lease:
        raise HTTPException(status_code=404, detail="Lease not found or does not belong to the specified tenant")

    # Validate payment method
    valid_methods = ["cash", "bank_transfer", "mobile_money", "check", "credit_card"]
    if payment.payment_method not in valid_methods:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid payment method. Must be one of: {', '.join(valid_methods)}"
        )

    try:
        # Create payment
        new_payment = Payments(
            tenant_id=payment.tenant_id,
            lease_id=payment.lease_id,
            payment_date=date.today(),
            amount=payment.amount,
            payment_method=payment.payment_method,
            payment_status="pending",
            transaction_reference=payment.transaction_reference,
            notes=payment.notes
        )

        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)

        return {
            "payment_id": new_payment.id,
            "tenant": f"{tenant.first_name} {tenant.last_name}",
            "lease_id": payment.lease_id,
            "amount": float(new_payment.amount),
            "status": new_payment.payment_status,
            "payment_date": new_payment.payment_date.isoformat(),
            "transaction_reference": new_payment.transaction_reference
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating payment: {str(e)}")

# Update payment status endpoint
@app.put("/payments/{payment_id}/status")
def update_payment_status(
    payment_id: int,
    status: str = Query(..., description="New payment status"),
    db: Session = Depends(get_db)
):
    """
    Update payment status
    """
    # Validate status
    valid_statuses = ["pending", "completed", "failed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    # Find the payment
    payment = db.query(Payments).filter(Payments.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Update the status
    old_status = payment.payment_status
    payment.payment_status = status
    
    # If marking as completed, update payment_date to today if it's still pending
    if status == "completed" and old_status == "pending":
        payment.payment_date = date.today()

    try:
        db.commit()
        db.refresh(payment)
        
        # Get tenant name for response
        tenant = db.query(Tenants).filter(Tenants.id == payment.tenant_id).first()
        tenant_name = f"{tenant.first_name} {tenant.last_name}" if tenant else "Unknown"

        return {
            "payment_id": payment.id,
            "old_status": old_status,
            "new_status": payment.payment_status,
            "tenant_name": tenant_name,
            "amount": float(payment.amount),
            "updated_at": payment.payment_date.isoformat() if payment.payment_date else None
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating payment status: {str(e)}")

# Get payment summary/statistics
@app.get("/payments-summary")
def get_payments_summary(db: Session = Depends(get_db)):
    """
    Get payment statistics summary
    """
    try:
        # Get total payments count
        total_payments = db.query(Payments).count()
        
        # Get payments by status
        completed_payments = db.query(Payments).filter(Payments.payment_status == "completed").count()
        pending_payments = db.query(Payments).filter(Payments.payment_status == "pending").count()
        failed_payments = db.query(Payments).filter(Payments.payment_status == "failed").count()
        cancelled_payments = db.query(Payments).filter(Payments.payment_status == "cancelled").count()
        
        # Get total amount (only completed payments)
        total_amount_result = db.query(func.sum(Payments.amount)).filter(
            Payments.payment_status == "completed"
        ).scalar()
        total_amount = float(total_amount_result) if total_amount_result else 0.0
        
        # Get monthly stats (current month)
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_payments = db.query(Payments).filter(
            extract('month', Payments.payment_date) == current_month,
            extract('year', Payments.payment_date) == current_year
        ).count()
        
        monthly_amount_result = db.query(func.sum(Payments.amount)).filter(
            extract('month', Payments.payment_date) == current_month,
            extract('year', Payments.payment_date) == current_year,
            Payments.payment_status == "completed"
        ).scalar()
        monthly_amount = float(monthly_amount_result) if monthly_amount_result else 0.0

        return {
            "total_payments": total_payments,
            "completed_payments": completed_payments,
            "pending_payments": pending_payments,
            "failed_payments": failed_payments,
            "cancelled_payments": cancelled_payments,
            "total_amount": total_amount,
            "monthly_payments": monthly_payments,
            "monthly_amount": monthly_amount
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching payment summary: {str(e)}")



@app.get("/payments/{payment_id}")
def get_payment_details(payment_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific payment
    """
    try:
        payment_query = db.query(
            Payments.id,
            Payments.tenant_id,
            Payments.lease_id,
            Payments.payment_date,
            Payments.amount,
            Payments.payment_method,
            Payments.payment_status,
            Payments.transaction_reference,
            Payments.notes,
            Payments.created_at,
            # Tenant information
            (Tenants.first_name + ' ' + Tenants.last_name).label('tenant_name'),
            Tenants.email.label('tenant_email'),
            Tenants.phone.label('tenant_phone'),
            # Property information
            Properties.name.label('property_name'),
            Properties.address.label('property_address'),
            # Lease information
            Leases.unit_number,
            Leases.rent_amount,
            Leases.lease_start,
            Leases.lease_end
        ).join(
            Tenants, Payments.tenant_id == Tenants.id
        ).join(
            Leases, Payments.lease_id == Leases.id
        ).join(
            Properties, Leases.property_id == Properties.id
        ).filter(Payments.id == payment_id).first()

        if not payment_query:
            raise HTTPException(status_code=404, detail="Payment not found")

        return {
            "id": payment_query.id,
            "tenant_id": payment_query.tenant_id,
            "lease_id": payment_query.lease_id,
            "tenant_name": payment_query.tenant_name,
            "tenant_email": payment_query.tenant_email,
            "tenant_phone": payment_query.tenant_phone,
            "property_name": payment_query.property_name,
            "property_address": payment_query.property_address,
            "unit_number": payment_query.unit_number,
            "payment_date": payment_query.payment_date.isoformat() if payment_query.payment_date else None,
            "amount": str(payment_query.amount),
            "payment_method": payment_query.payment_method,
            "payment_status": payment_query.payment_status,
            "transaction_reference": payment_query.transaction_reference,
            "notes": payment_query.notes,
            "rent_amount": str(payment_query.rent_amount) if payment_query.rent_amount else None,
            "lease_start": payment_query.lease_start.isoformat() if payment_query.lease_start else None,
            "lease_end": payment_query.lease_end.isoformat() if payment_query.lease_end else None,
            "created_at": payment_query.created_at.isoformat() if payment_query.created_at else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching payment details: {str(e)}")

# Delete payment (soft delete or hard delete based on your needs)
@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    """
    Delete a payment record
    """
    payment = db.query(Payments).filter(Payments.id == payment_id).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Only allow deletion of pending or failed payments
    if payment.payment_status in ["completed"]:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete completed payments. Please contact administrator."
        )
    
    try:
        db.delete(payment)
        db.commit()
        
        return {
            "message": "Payment deleted successfully",
            "payment_id": payment_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting payment: {str(e)}")

# Get payments by tenant
@app.get("/tenants/{tenant_id}/payments")
def get_tenant_payments(tenant_id: int, db: Session = Depends(get_db)):
    """
    Get all payments for a specific tenant
    """
    # Verify tenant exists
    tenant = db.query(Tenants).filter(Tenants.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    try:
        payments = db.query(
            Payments.id,
            Payments.payment_date,
            Payments.amount,
            Payments.payment_method,
            Payments.payment_status,
            Payments.transaction_reference,
            Payments.notes,
            Properties.name.label('property_name'),
            Leases.unit_number
        ).join(
            Leases, Payments.lease_id == Leases.id
        ).join(
            Properties, Leases.property_id == Properties.id
        ).filter(
            Payments.tenant_id == tenant_id
        ).order_by(Payments.payment_date.desc()).all()

        payments_list = []
        for payment in payments:
            payments_list.append({
                "id": payment.id,
                "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
                "amount": str(payment.amount),
                "payment_method": payment.payment_method,
                "payment_status": payment.payment_status,
                "transaction_reference": payment.transaction_reference,
                "notes": payment.notes,
                "property_name": payment.property_name,
                "unit_number": payment.unit_number
            })

        return {
            "tenant_id": tenant_id,
            "tenant_name": f"{tenant.first_name} {tenant.last_name}",
            "payments": payments_list,
            "total_payments": len(payments_list),
            "total_amount": sum(float(p["amount"]) for p in payments_list if payments_list)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tenant payments: {str(e)}")
    
    
    
@app.get("/payments/{payment_id}/invoice")
def get_invoice(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payments).filter(Payments.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    tenant = db.query(Tenants).filter(Tenants.id == payment.tenant_id).first()
    lease = db.query(Leases).filter(Leases.id == payment.lease_id).first()
    property = db.query(Properties).filter(Properties.id == lease.property_id).first()

    pdf_buffer = generate_invoice(payment, tenant, property)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=invoice_{payment.id}.pdf"}
    )



@app.get("/performance-metrics")
async def get_performance_metrics(db: Session = Depends(get_db)):
    """Calculate and return key performance metrics"""
    try:
        # 1. Occupancy Rate
        total_properties = db.query(Properties).filter(Properties.status == 1).count()
        occupied_properties = db.query(Leases).filter(
            and_(
                Leases.status == "active",
                Leases.start_date <= date.today(),
                Leases.end_date >= date.today()
            )
        ).count()
        
        occupancy_rate = (occupied_properties / total_properties * 100) if total_properties > 0 else 0
        
        # 2. Collection Rate (payments received vs payments due in current month)
        current_month_start = date.today().replace(day=1)
        if date.today().month == 12:
            next_month_start = date.today().replace(year=date.today().year + 1, month=1, day=1)
        else:
            next_month_start = date.today().replace(month=date.today().month + 1, day=1)
        
        # Total amount due this month
        total_due = db.query(func.sum(PaymentSchedule.amount_due)).filter(
            and_(
                PaymentSchedule.due_date >= current_month_start,
                PaymentSchedule.due_date < next_month_start
            )
        ).scalar() or 0
        
        # Total amount collected this month
        total_collected = db.query(func.sum(Payments.amount)).filter(
            and_(
                Payments.payment_date >= current_month_start,
                Payments.payment_date < next_month_start,
                Payments.payment_status == "completed"
            )
        ).scalar() or 0
        
        collection_rate = (total_collected / total_due * 100) if total_due > 0 else 0
        
        # 3. Maintenance Completion Rate (optional - based on a hypothetical maintenance table)
        # Since you don't have a maintenance table, we'll calculate based on payment schedules
        overdue_payments = db.query(PaymentSchedule).filter(
            and_(
                PaymentSchedule.due_date < date.today(),
                PaymentSchedule.status == "pending"
            )
        ).count()
        
        total_schedules = db.query(PaymentSchedule).count()
        maintenance_completion_rate = ((total_schedules - overdue_payments) / total_schedules * 100) if total_schedules > 0 else 100
        
        # 4. Tenant Satisfaction (mock calculation based on active tenants vs total tenants)
        total_tenants_ever = db.query(Tenants).count()
        active_tenants = db.query(Tenants).filter(Tenants.active_status == True).count()
        tenant_satisfaction = (active_tenants / total_tenants_ever * 100) if total_tenants_ever > 0 else 0
        
        return {
            "occupancy_rate": round(occupancy_rate, 1),
            "collection_rate": round(collection_rate, 1),
            "maintenance_completion_rate": round(maintenance_completion_rate, 1),
            "tenant_satisfaction": round(tenant_satisfaction, 1)
        }
        
    except Exception as e:
        logger.error(f"Error calculating performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate performance metrics")

# New endpoint - Recent Activities
@app.get("/recent-activities")
async def get_recent_activities(limit: int = 5, db: Session = Depends(get_db)):
    """Get recent activities from various sources"""
    try:
        activities = []
        
        # Recent lease signings
        recent_leases = db.query(Leases).join(Tenants).join(Properties).filter(
            Leases.created_at >= datetime.now() - timedelta(days=30)
        ).order_by(Leases.created_at.desc()).limit(limit).all()
        
        for lease in recent_leases:
            activities.append({
                "id": f"lease_{lease.id}",
                "type": "lease_signed",
                "description": f"New lease signed by {lease.tenant.first_name} {lease.tenant.last_name} for {lease.property.property_name} Unit {lease.property.unit_number}",
                "timestamp": lease.created_at.isoformat(),
                "tenant_name": f"{lease.tenant.first_name} {lease.tenant.last_name}",
                "amount": float(lease.monthly_rent)
            })
        
        # Recent payments
        recent_payments = db.query(Payments).join(Tenants).filter(
            and_(
                Payments.created_at >= datetime.now() - timedelta(days=30),
                Payments.payment_status == "completed"
            )
        ).order_by(Payments.created_at.desc()).limit(limit).all()
        
        for payment in recent_payments:
            activities.append({
                "id": f"payment_{payment.id}",
                "type": "payment_received",
                "description": f"Payment received from {payment.tenant.first_name} {payment.tenant.last_name}",
                "timestamp": payment.created_at.isoformat(),
                "tenant_name": f"{payment.tenant.first_name} {payment.tenant.last_name}",
                "amount": float(payment.amount)
            })
        
        # Recent tenant registrations
        recent_tenants = db.query(Tenants).filter(
            Tenants.created_at >= datetime.now() - timedelta(days=30)
        ).order_by(Tenants.created_at.desc()).limit(limit).all()
        
        for tenant in recent_tenants:
            activities.append({
                "id": f"tenant_{tenant.id}",
                "type": "tenant_moved_in",
                "description": f"New tenant {tenant.first_name} {tenant.last_name} registered",
                "timestamp": tenant.created_at.isoformat(),
                "tenant_name": f"{tenant.first_name} {tenant.last_name}"
            })
        
        # Recent overdue payments (as maintenance requests)
        overdue_schedules = db.query(PaymentSchedule).join(Leases).join(Tenants).filter(
            and_(
                PaymentSchedule.due_date < date.today(),
                PaymentSchedule.status == "pending"
            )
        ).order_by(PaymentSchedule.due_date.desc()).limit(limit).all()
        
        for schedule in overdue_schedules:
            activities.append({
                "id": f"overdue_{schedule.id}",
                "type": "maintenance_request",
                "description": f"Overdue payment from {schedule.lease.tenant.first_name} {schedule.lease.tenant.last_name}",
                "timestamp": schedule.created_at.isoformat(),
                "tenant_name": f"{schedule.lease.tenant.first_name} {schedule.lease.tenant.last_name}",
                "amount": float(schedule.amount_due)
            })
        
        # Sort all activities by timestamp and limit
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        activities = activities[:limit]
        
        return {"activities": activities}
        
    except Exception as e:
        logger.error(f"Error fetching recent activities: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch recent activities")


@app.get("/monthly-statistics")
async def get_monthly_statistics(db: Session = Depends(get_db)):
    """Get monthly statistics for the dashboard chart"""
    try:
        current_year = date.today().year
        monthly_data = []
        
        # Get data for each month of the current year
        for month in range(1, 13):
            month_start = date(current_year, month, 1)
            if month == 12:
                month_end = date(current_year + 1, 1, 1)
            else:
                month_end = date(current_year, month + 1, 1)
            
            # Monthly revenue from completed payments
            monthly_revenue = db.query(func.sum(Payments.amount)).filter(
                and_(
                    Payments.payment_date >= month_start,
                    Payments.payment_date < month_end,
                    Payments.payment_status == "completed"
                )
            ).scalar() or 0
            
            # Count of payments received in the month
            payments_count = db.query(func.count(Payments.id)).filter(
                and_(
                    Payments.payment_date >= month_start,
                    Payments.payment_date < month_end,
                    Payments.payment_status == "completed"
                )
            ).scalar() or 0
            
            # Calculate occupancy rate for the month (mid-month snapshot)
            mid_month = date(current_year, month, 15)
            total_properties = db.query(Properties).filter(Properties.status == 1).count()
            
            occupied_properties = db.query(Leases).filter(
                and_(
                    Leases.status == "active",
                    Leases.start_date <= mid_month,
                    Leases.end_date >= mid_month
                )
            ).count()
            
            occupancy_rate = (occupied_properties / total_properties * 100) if total_properties > 0 else 0
            
            # Convert payments count to revenue amount for visualization
            # This represents the total value of payments received
            payments_received = float(monthly_revenue)  # Same as revenue for now
            
            monthly_data.append({
                "month": month_start.strftime("%b"),
                "revenue": float(monthly_revenue),
                "payments_received": payments_received * 0.8,  # Slightly lower for visual distinction
                "occupancy_rate": round(occupancy_rate, 1)
            })
        
        return {"monthly_data": monthly_data}
        
    except Exception as e:
        logger.error(f"Error fetching monthly statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch monthly statistics")


@app.get("/property-demographics")
async def get_property_demographics(db: Session = Depends(get_db)):
    """Optimized property demographics query"""
    try:
        today = date.today()

        # Get aggregated data for all active properties
        lease_stats = (
            db.query(
                Leases.property_id,
                func.count(Leases.id).label("tenant_count"),
                func.avg(Leases.monthly_rent).label("average_rent")
            )
            .filter(
                and_(
                    Leases.status == "active",
                    Leases.start_date <= today,
                    Leases.end_date >= today
                )
            )
            .group_by(Leases.property_id)
            .all()
        )

        # Convert lease stats to a lookup dict
        lease_data = {row.property_id: row for row in lease_stats}

        # Fetch all active properties in one go
        properties = db.query(Properties).filter(Properties.status == 1).all()

        property_demographics = []

        for prop in properties:
            lease_info = lease_data.get(prop.id)
            tenant_count = lease_info.tenant_count if lease_info else 0
            average_rent = float(lease_info.average_rent or 0) if lease_info else float(prop.monthly_rent or 0)

            total_units = 1  # can change if you have unit count per property
            occupancy_rate = (tenant_count / total_units * 100) if total_units > 0 else 0

            area = prop.address.split(',')[-1].strip() if prop.address else "Unknown Area"

            property_demographics.append({
                "id": prop.id,
                "property_name": prop.property_name or f"Property {prop.unit_number}",
                "area": area,
                "tenant_count": tenant_count,
                "total_units": total_units,
                "occupancy_rate": round(min(occupancy_rate, 100), 1),
                "average_rent": round(average_rent, 2)
            })

        # Sort by tenant count (highest first)
        property_demographics.sort(key=lambda x: x["tenant_count"], reverse=True)

        return {"properties": property_demographics}

    except Exception as e:
        logger.error(f"Error fetching property demographics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch property demographics")
