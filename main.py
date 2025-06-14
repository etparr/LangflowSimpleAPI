import os
import pathlib

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import HTMLResponse

API_URL = (
    "https://api.langflow.astra.datastax.com/lf/4950f334-daf9-487b-8328-b475644f0117/"
    "api/v1/run/8254e480-727b-4e08-9731-808aa19cd24c"
)

ASTRA_TOKEN = os.getenv("ASTRA_API_TOKEN")
if not ASTRA_TOKEN:
    raise RuntimeError("Set the ASTRA_TOKEN environment variable with your application token.")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ASTRA_TOKEN}",
}

app = FastAPI()

app.mount("/static", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def root():
    return HTMLResponse((pathlib.Path("static") / "index.html").read_text(), status_code=200)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    payload = {
        "input_value": request.message,
        "output_type": "chat",
        "input_type": "chat",
    }
    try:
        resp = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        resp_json = resp.json()
        reply = (
            resp_json
            .get("outputs", [{}])[0]
            .get("outputs", [{}])[0]
            .get("outputs", {})
            .get("message", {})
            .get("message", "No reply found")
        )
        return JSONResponse({"reply": reply})
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
