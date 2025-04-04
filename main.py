from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import logging

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


@app.post('/webhooks')
async def handle_webhook(request: Request):
    data = await request.json()
    print(data)
    logging.info("Received webhook event: %s", data)
    return {"status": "received"}