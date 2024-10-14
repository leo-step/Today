from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
from bson import ObjectId

load_dotenv()

client = MongoClient(os.getenv("MONGO_CONN"))
db = client['today']
collection = db['conversations']

docs = collection.find({"time": {"$gt": 1726990039}})

def convert_objectid(doc):
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc

with open("conversations_dump.json", "w") as fp:
    json.dump([convert_objectid(doc) for doc in docs], fp)

print("Conversations have been written to conversations_dump.json")
