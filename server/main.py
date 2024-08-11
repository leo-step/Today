from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from mixpanel import Mixpanel
from pydantic import BaseModel
from typing import Any
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

@app.get("/api/extension/widget-data")
async def index():
    client = pymongo.MongoClient(os.getenv("DB_CONN"))
    db = client[os.getenv("DATABASE")]
    data = db.widgets.find_one({'_id': 'data'})
    return data

@app.post("/api/track")
async def track(data: Event):
    mp.track(data.uuid, data.event, data.properties)
