from openai import OpenAI
from dotenv import load_dotenv
import pymongo
import requests
from tqdm import tqdm
import os

load_dotenv()

pc_mongo_client = pymongo.MongoClient(os.getenv("PRINCETON_COURSES_MONGO_CONN"))["princetoncourses-production"]
db_client = pymongo.MongoClient(os.getenv("CHATBOT_MONGO_CONN"))["today"]
openai_client = OpenAI()

def get_course_ids():
    semester = 1252
    results = pc_mongo_client["courses"].find({"semester": semester})
    return [doc["_id"] for doc in results]

def get_course_data(course_id):
    headers = {
        "Authorization": "Bearer " + os.getenv("COURSES_API_KEY")
    }
    response = requests.get(f"https://www.princetoncourses.com/api/course/{course_id}", headers=headers)
    return response.json()

def get_text(data):
    comments = list(map(lambda x: x["comment"], data["evaluations"]["comments"]))[:3]
    comments_text = '\n'.join(comments)
    return f'''{data["commonName"]} - {data["title"]}

    {data["description"]}

    {comments_text}'''

def get_embedding(query_text, model="text-embedding-3-large", dimensions=256):
   query_text = query_text.replace("\n", " ")
   return openai_client.embeddings.create(input = [query_text], model=model, dimensions=dimensions).data[0].embedding

if __name__ == "__main__":
    course_ids = get_course_ids()
    for course_id in tqdm(course_ids):
        data = get_course_data(course_id)
        text = get_text(data)
        embedding = get_embedding(text)
        data["text"] = text
        data["embedding"] = embedding
        db_client["courses"].insert_one(data)
