from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from dotenv import load_dotenv
from mixpanel import Mixpanel
from pydantic import BaseModel
from tools import tools, choose_tool_and_rewrite, invoke_tool
from response import generate_response
from models import ChatQueryInput
from typing import Any
from memory import Memory, ToolInvocation, MessageType
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

@app.post("/api/chat")
async def chat(query: ChatQueryInput = Body(...)):
    memory = Memory(query.uuid, query.session_id)

    tool, query_rewrite = choose_tool_and_rewrite(tools, memory, query.text)
    tool_result = invoke_tool(tool, query_rewrite)
    tool_use: ToolInvocation = {
        "tool": tool,
        "input": query_rewrite,
        "output": tool_result
    }

    memory.add_message(MessageType.HUMAN, query.text)
    mp.track(query.uuid, "chat", {'session_id': query.session_id})

    return StreamingResponse(
        generate_response(memory, tool_use), 
    media_type="text/plain")
