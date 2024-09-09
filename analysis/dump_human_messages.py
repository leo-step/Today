from pymongo import MongoClient
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_CONN"))
db = client['today']
collection = db['conversations']

ny_tz = pytz.timezone('America/New_York')

docs = collection.find().sort("time", -1)

for doc in docs:
    print(f"Conversation UUID: {doc['uuid']}")
    # print(f"Session ID: {doc['session_id']}")
    # print(f"Conversation Timestamp: {datetime.fromtimestamp(doc['time']).astimezone(ny_tz).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    # print("Human Messages:")

    for message in doc['messages']:
        if message['type'] == 'human':
            message_time = datetime.fromtimestamp(message['time']).astimezone(ny_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
            print(f"[Human] ({message_time}): {message['content']}")

    print("\n--------------------\n")

print("All human messages have been printed.")
