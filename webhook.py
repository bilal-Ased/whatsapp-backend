from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import hmac
import hashlib
import os
from nylas import Client
from dataclasses import dataclass
import pendulum

# Initialize Nylas client
nylas = Client(
    api_key = os.getenv('V3_API_KEY')
)

# Get today’s date
today = pendulum.now()

# Create the FastAPI app
app = FastAPI()

# Webhook storage
webhooks = []

@dataclass
class Webhook:
    _id: str
    date: str
    title: str
    description: str
    participants: str
    status: str

# Pydantic model for webhook data
class WebhookData(BaseModel):
    data: dict

@app.get("/webhook")
async def webhook_verification(challenge: str):

    print(" * Nylas connected to the webhook!")
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content=challenge)

