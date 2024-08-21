from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from dotenv import load_dotenv
from mixpanel import Mixpanel
from pydantic import BaseModel
from retrievers import retrieve_crawl, retrieve_emails
from tools import rewrite_and_choose_tool
from response import generate_response
from models import ChatQueryInput
from typing import Any
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
    
    start_time = time.time()
    user_conversations.update_one(document, update_fields, upsert=True)
    end_time = time.time()
    print(end_time-start_time)

    start_time = time.time()
    query_rewrite, tool = rewrite_and_choose_tool(query.text) # 0.5s average (no rewrite)
    end_time = time.time()
    print(end_time-start_time)
    

    start_time = time.time()
    documents = [] # 1-1.5s average
    if tool == "Crawl":
        documents = retrieve_crawl(query_rewrite)
    elif tool == "Emails":
        documents = retrieve_emails(query_rewrite)
    end_time = time.time()
    print(end_time-start_time)

    start_time = time.time()
    mp.track(query.uuid, "chat", {'session_id': query.session_id})
    end_time = time.time()
    print(end_time-start_time)

    return StreamingResponse(generate_response(query_rewrite, documents), media_type="text/plain")
