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

with open('conversations_dump.txt', 'w') as file:
    for doc in docs:
        file.write(f"Conversation UUID: {doc['uuid']}\n")
        file.write(f"Session ID: {doc['session_id']}\n")
        file.write(f"Timestamp: {datetime.fromtimestamp(doc['time']).astimezone(ny_tz).strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
        file.write("Messages:\n")
        
        for message in doc['messages']:
            message_time = datetime.fromtimestamp(message['time']).astimezone(ny_tz).strftime('%Y-%m-%d %H:%M:%S %Z')
            file.write(f"[{message['type'].capitalize()}] ({message_time}): {message['content']}\n")
        
        file.write("\n--- End of Conversation ---\n\n")

print("Conversations have been written to conversations_dump.txt")
