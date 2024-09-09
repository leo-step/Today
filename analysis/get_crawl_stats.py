from pymongo import MongoClient
from collections import Counter
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_CONN"))
db = client['today']  # Replace with your actual database name
collection = db['crawl']  # Replace with your actual collection name

# 1. Number of documents in the collection
num_documents = collection.count_documents({})
print(f"Number of documents in the collection: {num_documents}")

# Function to calculate percentages over a specified field
def calculate_field_percentages(collection, field, filter_query=None):
    # If no filter query is provided, use an empty filter
    if filter_query is None:
        filter_query = {}

    # Aggregate data based on the specified field
    pipeline = [
        {"$match": filter_query},  # Apply filter if provided
        {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},  # Group by the field and count occurrences
        {"$sort": {"count": -1}}  # Sort by count in descending order
    ]
    
    # Run the aggregation pipeline
    results = list(collection.aggregate(pipeline))
    total_count = sum(result['count'] for result in results)  # Total number of occurrences

    # Print the percentages
    print(f"Percentages for field '{field}':")
    for result in results:
        percentage = (result['count'] / total_count) * 100
        field_value = result['_id'] if result['_id'] is not None else "None"
        print(f"Value: {field_value}, Count: {result['count']}, Percentage: {percentage:.2f}%")

# Example usage:
# Specify the field you want to calculate percentages for
field_name = "source"  # Replace with your field of interest

calculate_field_percentages(collection, field_name)
