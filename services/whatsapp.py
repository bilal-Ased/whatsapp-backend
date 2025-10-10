import httpx
import os

WHATSAPP_API_URL = "https://graph.facebook.com/v20.0/486982054488039/messages"
WHATSAPP_TOKEN = "EAANTaTeKBwIBPuPpZCKNDte2pYRLqJpHGDONak8Yx9OViXSryIpCAz2wZA2dTRlZA4E4rSUECFxlCHHLGXixAQZBX53f5KxXCS2VOgrcHfd2g9ebzi64jsZAPFaYYmxurhnZBZAvEMg1Vk9fMccMNIa0yZAFn9UARIK1Mm5NghgtPyuSAI0JUiqt40ANw2HvnmDbgShOBRoxLZCRGnRx8paItuRZB2lE3UZA37nZBDUl7Xmxb0gzMYkZBQMKyLdpoMw5L1QZDZD"

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
