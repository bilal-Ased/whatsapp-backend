from fastapi import FastAPI, Depends, Query
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import CustomersTable,Tickets
from models import MobileBankingData,CreditCardData
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import joinedload
from fastapi.middleware.cors import CORSMiddleware
from schemas.customer import CustomerCreate, CustomerUpdate,TicketCreate
from schemas.customer import MobileCustomerData,CreditCardCustomerData
from sqlalchemy.exc import IntegrityError
from typing import Optional




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