from fastapi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI()

@app.get("/webhook")
async def verify_webhook(request: Request):
    challenge = request.query_params.get("challenge")
    if challenge:
        # Must return plain text (no quotes, no JSON, no chunking)
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Missing challenge", media_type="text/plain", status_code=400)
