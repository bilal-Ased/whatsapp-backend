from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Rent Reminder Email Service")

# Email configuration - set these in your .env file
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM", "mughalbilal89@gmail.com")
EMAIL_SENDER_NAME = os.getenv("EMAIL_SENDER_NAME", "Silverfox Management")

class Tenant(BaseModel):
    name: str
    email: EmailStr

TENANTS = [
    Tenant(name="network", email="networkingmughal@gmail.com"),
    Tenant(name="Vertex", email="vertexconnects@gmail.com"),
    Tenant(name="Sidra", email="sidram992@gmail.com "),
    Tenant(name="Bilal", email="mughalbilal89@gmail.com"),
    Tenant(name="Intisar", email="intisarof1997@gmail.com")
]

def send_email(tenant: Tenant):
    """Sends a personalized email to a tenant."""
    message = MIMEMultipart()
    message["From"] = f"{EMAIL_SENDER_NAME} <{EMAIL_FROM}>"
    message["To"] = tenant.email
    message["Subject"] = "Rent Payment Reminder - April 2025"
    
    email_body = f"""
Dear {tenant.name},

We hope you are enjoying your stay at Grand Premier Apartments. This is a kind reminder that your April rent is due by 5th April 2025. If you have already made the payment, kindly confirm by sharing the confirmation message to this email for our records.

Kindly note that the landlord has updated her account details. Moving forward, please use the following payment details:
Account Name: Brenda Aloo Okwiri
Account Number: 0100465194900
Bank: Standard Chartered Bank, Yaya Branch

For payments via Paybill:
Paybill Number: 329329
Account Number: 0100465194900

Kind regards,
Silverfox Management
    """
    
    # Attach email body
    message.attach(MIMEText(email_body, "plain"))
    
    try:
        # Connect to SMTP server
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(message)
        return {"status": "success", "recipient": tenant.email}
    except Exception as e:
        print(f"Failed to send email to {tenant.email}: {str(e)}")
        return {"status": "error", "recipient": tenant.email, "error": str(e)}

async def send_emails_in_background(tenants: List[Tenant]):
    """Send emails to all tenants in the background."""
    results = []
    for tenant in tenants:
        result = send_email(tenant)
        results.append(result)
    return results

@app.post("/send-rent-reminders")
async def send_rent_reminders(background_tasks: BackgroundTasks):
    """
    Send rent reminder emails to all tenants in the hardcoded list
    """
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        raise HTTPException(
            status_code=500, 
            detail="Email configuration is incomplete. Please set EMAIL_USERNAME and EMAIL_PASSWORD environment variables."
        )
    
    # Queue the email sending process in the background
    background_tasks.add_task(send_emails_in_background, TENANTS)
    
    return {
        "message": f"Rent reminder emails are being sent to {len(TENANTS)} tenants",
        "status": "processing",
        "tenants": [{"name": tenant.name, "email": tenant.email} for tenant in TENANTS]
    }

@app.get("/tenants")
async def list_tenants():
    """Get the list of tenants who will receive rent reminders."""
    return {"tenants": [{"name": tenant.name, "email": tenant.email} for tenant in TENANTS]}

@app.get("/")
async def root():
    """Root endpoint to check if the API is running."""
    return {"message": "Rent Reminder Email Service is running"}

# Example for testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)