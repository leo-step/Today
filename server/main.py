from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from dotenv import load_dotenv
from mixpanel import Mixpanel
from pydantic import BaseModel
from agents.tay_agent import tay_agent, AsyncCallbackHandler, run_call
from models.chat_query import ChatQueryInput, ChatQueryOutput
from typing import Any
import asyncio
import pymongo
import os

load_dotenv()
app = FastAPI()
mp = Mixpanel(os.getenv("MIXPANEL"))

class Event(BaseModel):
    uuid: str
    event: str
    properties: Any

origins = [
    "*" # fix later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== EXTENSION ==========

@app.get("/api/extension/widget-data")
async def index():
    client = pymongo.MongoClient(os.getenv("DB_CONN"))
    db = client[os.getenv("DATABASE")]
    data = db.widgets.find_one({'_id': 'data'})
    data["timestamp"] = str(datetime.now(timezone.utc))
    return data

@app.post("/api/track")
async def track(data: Event):
    mp.track(data.uuid, data.event, data.properties)


# ========== CHATBOT ==========

async def create_gen(query: str, stream_it: AsyncCallbackHandler):
    task = asyncio.create_task(run_call(query, stream_it))
    async for token in stream_it.aiter():
        yield token
    await task

@app.get("/api/chat")
async def chat(query: ChatQueryInput = Body(...)):
    stream_it = AsyncCallbackHandler()
    gen = create_gen(query.text, stream_it)
    return StreamingResponse(gen, media_type="text/event-stream")
