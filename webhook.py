from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

app = FastAPI()


# Pydantic model for webhook data
class WebhookData(BaseModel):
    data: dict

@app.get("/webhook")
async def webhook_verification(challenge: str):

    print(" * Nylas connected to the webhook!")
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content=challenge)

@app.post("/webhook")
async def nylas_webhook(request:Request):
    data = await request.json()
    print(data)
    





