import httpx
import os

WHATSAPP_API_URL = "https://graph.facebook.com/v20.0/486982054488039/messages"
WHATSAPP_TOKEN = "EAANTaTeKBwIBPUeBhz1pIZAjkDsN00NFDve8YCTpMywn0OLH6UEEULVW6QOEmOYNYro0Ef98oJlHXiACEMSZCPYSkU3o4Hz5EBLXn8AAAO9041YQDpYCbavYDp9P3uwdEuQZBjZBlhSJ6zJ3ZBgtZAaM92OpZCyRZAF6OJdkseFVoXCZCMo09ft93hFglmNU9nIQBpchrs1fZC571ddaZAVMcDeICPnT0Fq5AZAD1zhEsi9AtZBryLA01rxeniNSr4P9j1gZDZD"

async def send_payment_confirmation(
    to: str,
    customer_name: str,
    amount: str,
    month: str,
    invoice_number: str,
    payment_date: str,
    unit: str
):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": "payment_confirmation",
            "language": {"code": "en_US"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": customer_name},
                        {"type": "text", "text": amount},
                        {"type": "text", "text": month},
                        {"type": "text", "text": invoice_number},
                        {"type": "text", "text": payment_date},
                        {"type": "text", "text": unit},
                    ]
                }
            ]
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(WHATSAPP_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
