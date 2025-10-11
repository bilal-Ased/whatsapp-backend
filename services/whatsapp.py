import httpx
import os

WHATSAPP_API_URL = "https://graph.facebook.com/v20.0/486982054488039/messages"
WHATSAPP_TOKEN = "EAANTaTeKBwIBPj5Y5p0Wb5uOneO2cKcGhZBhsiJwxJlGyZCZCSlBkHBeaEIFTZCrcOSHL4wY8PZAaEvVYGDlJSyQVvZBZArs3NV3xYKLeW4IoIlmRWy6HsLhizahtdCf7SUBTjcmgpsktmZCSeXw2izuCDtPauyKCySopKm0gcZC9ZCsQjSUwoG2hZCA1KkND5hMl6oeWnM5Rv0Fh82loECo2XQRuIZCi4eeIyN6ppTdZCX8iZCECPsdrF45cumFZC82TZAcmQZDZD"

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
