from pymongo import MongoClient
from preprocess import is_eating_club
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_CONN"))
# Define collection and index name
db_name = "today"
collection_name = "crawl"
collection = client[db_name][collection_name]

cursor = collection.find({
    "source": "email"
})

for doc in cursor:
    # Compute the new field value
    eating_club = is_eating_club(doc["text"])
    # Update the document with the new field
    if eating_club:
        doc["_id"] += "__ec"
        doc["source"] = "eatingclub"
        collection.insert_one(doc)

    print(f"Updated document with _id: {doc['_id']}")

print('Migration completed')
