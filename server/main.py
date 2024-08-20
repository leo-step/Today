from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from dotenv import load_dotenv
from mixpanel import Mixpanel
from pydantic import BaseModel
from agents.tay_agent import AsyncCallbackHandler, get_agent_run_call
from models.chat_query import ChatQueryInput
from typing import Any
import asyncio
import pymongo
import os
import time

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

async def create_gen(query: str, stream_it: AsyncCallbackHandler, run_call):
    task = asyncio.create_task(run_call(query, stream_it))
    async for token in stream_it.aiter():
        yield token
    await task

@app.post("/api/chat")
async def chat(query: ChatQueryInput = Body(...)):
    client = pymongo.MongoClient(os.getenv("MONGO_CONN"))
    user_conversations = client["today"]["user_conversations"]
    document = {
        'uuid': query.uuid,
        'session_id': query.session_id,
        'time': int(time.time())
    }
    update_fields = {
        '$set': document
    }

    user_conversations.update_one(document, update_fields, upsert=True)

    stream_it = AsyncCallbackHandler()
    agent_run_call = get_agent_run_call(query.uuid, query.session_id)
    gen = create_gen(query.text, stream_it, agent_run_call)

    mp.track(query.uuid, "chat", {'session_id': query.session_id})

    return StreamingResponse(gen, media_type="text/event-stream")
