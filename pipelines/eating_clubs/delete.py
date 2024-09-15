import pymongo
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Function to delete documents with specific criteria
def delete_recent_eatingclub_documents(db, collection_name):
    collection = db[collection_name]
    print(collection.count_documents({}))

    # Calculate the time 10 minutes ago
    ten_minutes_ago = int((datetime.utcnow() - timedelta(minutes=10)).timestamp())

    # Define the query to find documents with "source": "eatingclub" and "time" within the last 10 minutes
    query = {
        "source": "eatingclub",
        "time": {"$gte": 1726421753}
    }

    # Delete the matching documents and get the result
    result = collection.delete_many(query)

    # Print how many documents were deleted
    print(f"Documents deleted: {result.deleted_count}")

if __name__ == "__main__":
    # MongoDB connection details
    load_dotenv()
    print(os.getenv("MONGO_CONN"))
    client = pymongo.MongoClient(os.getenv("MONGO_CONN"))
    db = client["today"]  # Replace with your database name

    # Collection name where the documents are stored
    collection_name = "crawl"  # Replace with your collection name

    # Delete documents and print the count
    delete_recent_eatingclub_documents(db, collection_name)
