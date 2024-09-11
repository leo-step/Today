from pymongo import MongoClient
from preprocess import get_expiry_time
import os

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
    expiry_time = get_expiry_time(doc["text"], doc["time"])
    # Update the document with the new field
    collection.update_one(
        {'_id': doc['_id']},
        {'$set': {'expiry': expiry_time}}
    )

    print(f"Updated document with _id: {doc['_id']}")

print('Migration completed')
