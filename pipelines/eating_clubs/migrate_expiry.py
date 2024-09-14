from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_CONN"))
# Define collection and index name
db_name = "today"
collection_name = "crawl"
collection = client[db_name][collection_name]

# Define the expiry time
expiry_time = 2147483647

# Perform an update_many operation where documents don't already have the 'expiry' field
result = collection.update_many(
    {'expiry': {'$exists': False}},  # Only update documents where 'expiry' does not exist
    {'$set': {'expiry': expiry_time}}
)

print(f"Updated {result.modified_count} documents.")
print('Migration completed')
