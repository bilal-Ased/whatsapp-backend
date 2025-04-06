from fastapi import FastAPI, Request,HTTPException,Depends
from fastapi.responses import PlainTextResponse
import logging
from sqlalchemy.orm import Session
from models import Contact, WhatsappMessage
from database import SessionLocal, init_db
from datetime import datetime

app = FastAPI()


VERIFY_TOKEN = "meatyhamhock"  # This should match what you set in Meta
logging.basicConfig(level=logging.INFO)


@app.get("/webhooks")
async def verify_webhook(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_challenge = request.query_params.get("hub.challenge")
    hub_verify_token = request.query_params.get("hub.verify_token")

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    else:
        return PlainTextResponse(content="Verification failed", status_code=403)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/webhooks")
async def handle_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    logging.info("Received webhook event: %s", data)
    
    try:
        # The structure comes directly from the "value" field
        value = data.get("value", {})
        
        # Extract contact information and message
        if value.get("contacts") and len(value.get("contacts", [])) > 0:
            phone_number = value.get("contacts", [])[0].get("wa_id")
            contact_name = value.get("contacts", [])[0].get("profile", {}).get("name", "Unknown")
        else:
            logging.error("No contacts found in webhook data")
            return {"status": "error", "message": "No contacts found in webhook data"}
            
        if value.get("messages") and len(value.get("messages", [])) > 0:
            message = value.get("messages", [])[0]
            message_id = message.get("id")
            message_body = message.get("text", {}).get("body") if message.get("type") == "text" else None
            direction = "incoming"
        else:
            logging.error("No messages found in webhook data")
            return {"status": "error", "message": "No messages found in webhook data"}

        # Check if the contact exists in the database
        contact = db.query(Contact).filter(Contact.phone_number == phone_number).first()
        
        if not contact:
            # If contact doesn't exist, create a new one
            contact = Contact(phone_number=phone_number, name=contact_name, email=None)
            db.add(contact)
            db.commit()
            db.refresh(contact)
        
        # Create a new WhatsappMessage record
        whatsapp_message = WhatsappMessage(
            contact_id=contact.id,
            message_id=message_id,
            direction=direction,
            message_body=message_body,
            sent_at=datetime.utcnow(),
        )
        
        db.add(whatsapp_message)
        db.commit()
        
        logging.info("Message processed successfully for contact %s", contact.phone_number)
        return {"status": "received", "message": "Webhook processed successfully."}
    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing webhook: {str(e)}")
    
@app.get("/customers")
def get_customers(db: Session = Depends(get_db)):
    try:
        customers = db.query(Contact).all()  # Query to fetch all contacts
        if not customers:
            raise HTTPException(status_code=404, detail="No customers found.")
        return customers  # Returns a list of customers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching customers: {str(e)}")
    