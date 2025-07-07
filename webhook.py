from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse


app = FastAPI()


# Pydantic model for webhook data
class WebhookData(BaseModel):
    data: dict

@app.get("/webook")
async def webhook_verification(challenge: str):
    print(f"✅ Received verification challenge: {challenge}")
    return PlainTextResponse(content=challenge)

@app.post("/webhook")
async def webhook_event(request: Request):
    payload = await request.json()
    print("📬 Received event:", payload)
    return {"status": "ok"}

    





