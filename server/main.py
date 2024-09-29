from fastapi import FastAPI, Body, Query
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
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
import uuid

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

# ========== UI ==========

# app = FastAPI() #duplicate app call overwrites other things no?

app.mount("/static", StaticFiles(directory="dist"), name="static")

@app.get("/")
async def serve_react():
    return FileResponse("dist/index.html")

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


# ========== iOS SHORTCUT ==========

@app.get("/api/ios_chat")
async def ios_chat(query: str = Query(..., description="The user's chat query")):
    # generate a random UUID and session ID
    temp_uuid = str(uuid.uuid4())
    temp_session_id = str(uuid.uuid4())

    memory = Memory(temp_uuid, temp_session_id)

    tool, query_rewrite = choose_tool_and_rewrite(tools, memory, query)
    tool_result = invoke_tool(tool, query_rewrite)
    tool_use: ToolInvocation = {
        "tool": tool,
        "input": query_rewrite,
        "output": tool_result
    }

    memory.add_message(MessageType.HUMAN, query)
    mp.track(temp_uuid, "ios_chat", {'session_id': temp_session_id})

    # use list to collect the repsonse chunks
    response_chunks = []
    async for chunk in generate_response(memory, tool_use):
        response_chunks.append(chunk)
    
    # join all chunks into single response
    full_response = ''.join(response_chunks)
    
    return {"response": full_response}
