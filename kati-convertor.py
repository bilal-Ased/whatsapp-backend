from fastapi import FastAPI, Request
import logging
from datetime import datetime
import json
import requests

app = FastAPI()

# Log to terminal
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


@app.post("/send-survey")
async def send_survey_endpoint(request: Request):
    try:
        # 1. Parse ticket from request
        ticket = await request.json()
        logging.info(f"✅ Received ticket:\n{json.dumps(ticket, indent=2)}")

        # 2. Transform into survey format
        payload = transform_ticket_to_survey(ticket)
        logging.info(f"📦 Transformed payload:\n{json.dumps(payload, indent=2)}")

        # 3. Send survey payload
        response = requests.post(
            "https://ratemyservice.co.ke/send-survey",
            json=payload,
            timeout=10  # optional but recommended
        )

        # 4. Log API response
        logging.info(f"📨 Survey API responded: {response.status_code} - {response.text}")

        return {
            "status": "sent",
            "response_code": response.status_code,
            "survey_response": response.text
        }

    except requests.exceptions.RequestException as re:
        logging.error(f"❌ RequestException during POST: {re}")
        return {
            "status": "error",
            "message": str(re)
        }

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


def transform_ticket_to_survey(ticket):
    return {
        "apikey": "0SKOSSG0xvLDLsmNOH61QBaHYW7CexpFF1XrWpSsXMJz0M2mWA614",
        "profileId": "2408",
        "name": ticket.get("customer_name"),
        "number": format_number(ticket.get("customer_phone")),
        "branch": ticket.get("location") or "Unknown",
        "agent": ticket.get("assigned_to") or "Unassigned",
        "product": ticket.get("asset_name") or "N/A",
        "date": format_unix_date(ticket.get("ticket_closure_date"))
    }


def format_number(phone):
    try:
        phone = phone.strip()
        if phone.startswith("0"):
            return "+254" + phone[1:]
        elif phone.startswith("254") and not phone.startswith("+"):
            return "+" + phone
        elif not phone.startswith("+254"):
            return "+254" + phone
        return phone
    except Exception:
        return "+254000000000"


def format_unix_date(timestamp):
    try:
        timestamp = int(str(timestamp)[:10])  # trim to 10-digit seconds
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
    except Exception as e:
        logging.warning(f"⚠️ Invalid timestamp: {timestamp} — Error: {e}")
        return None
