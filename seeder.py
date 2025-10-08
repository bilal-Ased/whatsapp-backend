from datetime import date
from database import SessionLocal, engine
from models import CustomersTable, MobileBankingData, CreditCardData  # adjust import based on your structure
import random
import string

# Create a new session
session = SessionLocal()

# Function to generate random string for names, etc.
def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Create 30 dummy customers
for _ in range(30):
    first_name = generate_random_string(5)
    middle_name = generate_random_string(2)
    last_name = generate_random_string(5)
    mobile_number = f"07{random.randint(10000000, 99999999)}"
    alternate_phone_number = f"07{random.randint(10000000, 99999999)}"
    identification_no = f"ID{random.randint(10000000, 99999999)}"
    account_number = f"{random.randint(1000000000, 9999999999)}"
    branch_name = f"Branch {random.choice(['Downtown', 'Uptown', 'Midtown'])}"
    email = f"{first_name.lower()}.{last_name.lower()}@example.com"
    secondary_email = f"{first_name.lower()}.{last_name.lower()}@alt.com"
    branch_code = f"0{random.randint(1, 9)}"
    cif = f"CIF{random.randint(100000, 999999)}"
    age = random.randint(18, 65)
    gender = random.choice(['Male', 'Female'])
    status = random.choice(['Active', 'Inactive'])
    nationality = random.choice(['Kenyan', 'Ugandan', 'Tanzanian'])
    physical_address = f"{random.randint(1, 999)} River Road"
    postal_address = f"P.O. Box {random.randint(1000, 9999)}"
    date_of_birth = date(random.randint(1955, 2005), random.randint(1, 12), random.randint(1, 28))

    # Create a dummy customer record
    customer = CustomersTable(
        first_name=first_name,
        middle_name=middle_name,
        last_name=last_name,
        mobile_number=mobile_number,
        alternate_phone_number=alternate_phone_number,
        identification_no=identification_no,
        account_number=account_number,
        branch_name=branch_name,
        email=email,
        secondary_email=secondary_email,
        branch_code=branch_code,
        cif=cif,
        age=age,
        gender=gender,
        has_fdr=True,
        status=status,
        nationality=nationality,
        physical_address=physical_address,
        postal_address=postal_address,
        date_of_birth=date_of_birth,
    )

    # Add related mobile banking data
    mobile_data = MobileBankingData(
        identification_no=customer.identification_no,
        mobile_number=customer.mobile_number,
        pinstatus="Active",
        account_number=customer.account_number,
        bank_branch_code=branch_code,
        pin_suppress=False,
        bank_branch_name=branch_name,
    )

    # Add related credit card data
    credit_card_data = CreditCardData(
        identification_no=customer.identification_no,
        mobile_number=customer.mobile_number,
        card_number=f"411111111111{random.randint(1000, 9999)}",
        cif=customer.cif,
        card_limit=random.randint(10000, 100000),
        card_status="Active",
    )

    # Set relationships
    customer.mobile_banking_data.append(mobile_data)
    customer.credit_card_data.append(credit_card_data)

    # Add and commit to DB in each loop iteration
    session.add(customer)

# Commit all the records at once after the loop
session.commit()

# Close the session
session.close()

print("30 dummy records inserted!")
