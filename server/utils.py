from clients import openai_client
from dotenv import load_dotenv
import time
import os

load_dotenv()

def get_embedding(query_text, model="text-embedding-3-large", dimensions=256):
   query_text = query_text.replace("\n", " ")
   return openai_client.embeddings.create(input = [query_text], model=model, dimensions=dimensions).data[0].embedding

def with_timing(func):
    if os.getenv("DEBUG") != "1":
        return func
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"[TIMING] '{func.__name__}' executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper
