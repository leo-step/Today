from pymongo import MongoClient
from collections import Counter
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_CONN"))
db = client['today']  # Replace with your actual database name
collection = db['conversations']  # Replace with your actual collection name

# 1. Number of documents in the collection
num_documents = collection.count_documents({})
print(f"Number of documents in the collection: {num_documents}")

# 2. Percentages for different tool uses for AI messages
pipeline_tool_use = [
    {"$unwind": "$messages"},
    {"$match": {"messages.type": "ai"}},
    {"$group": {"_id": "$messages.tool_use.tool", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
tool_use_stats = list(collection.aggregate(pipeline_tool_use))
total_ai_messages = sum(item['count'] for item in tool_use_stats)

print("\nTool Use Percentages for AI Messages:")
for tool in tool_use_stats:
    percentage = (tool['count'] / total_ai_messages) * 100
    tool_name = tool['_id'] if tool['_id'] is not None else "None"
    print(f"Tool Use: {tool_name}, Count: {tool['count']}, Percentage: {percentage:.2f}%")

# 3. Distribution of conversation length (total messages per conversation)
pipeline_conversation_length = [
    {"$project": {"conversation_length": {"$size": "$messages"}}}
]
conversation_lengths = list(collection.aggregate(pipeline_conversation_length))
length_counter = Counter(item['conversation_length'] for item in conversation_lengths)

print("\nDistribution of Conversation Lengths:")
for length, count in length_counter.items():
    print(f"Conversations with {length} messages: {count}")

# 4. Number of conversations by user and analysis
pipeline_conversations_by_user = [
    {"$group": {"_id": "$uuid", "conversation_count": {"$sum": 1}}}
]
conversations_by_user = list(collection.aggregate(pipeline_conversations_by_user))
unique_users = len(conversations_by_user)
users_more_than_once = sum(1 for user in conversations_by_user if user['conversation_count'] > 1)

print(f"\nNumber of Unique Users: {unique_users}")
print(f"Number of Users with More Than One Conversation: {users_more_than_once}")

# 5. Percentage of conversations with more than 2 messages
conversations_with_more_than_2 = sum(1 for length in conversation_lengths if length['conversation_length'] > 2)
percentage_more_than_2 = (conversations_with_more_than_2 / num_documents) * 100

print(f"Percentage of Conversations with More Than 2 Messages: {percentage_more_than_2:.2f}%")
