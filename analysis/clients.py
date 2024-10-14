from openai import OpenAI
from openai import AsyncOpenAI
from dotenv import load_dotenv
import pymongo
import os

load_dotenv()

db_client = pymongo.MongoClient(os.getenv("MONGO_CONN"))["today"]
openai_client = OpenAI()
