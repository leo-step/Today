from clients import openai_client, async_openai_client
from dotenv import load_dotenv
from typing import List
import time
import os
import json

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

def system_prompt(func):
    def wrapper(*args, **kwargs):
        text = func(*args, **kwargs)
        # if os.getenv("DEBUG") == "1":
        #     print("[PROMPT]", text)
        return {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
    return wrapper

def user_prompt(func):
    def wrapper(*args, **kwargs):
        text = func(*args, **kwargs)
        # if os.getenv("DEBUG") == "1":
        #     print("[PROMPT]", text)
        return {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
    return wrapper

def openai_json_response(messages: List, model="gpt-4o-mini", temp=1, max_tokens=1024):
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json_object"
        }
    )
    return json.loads(response.choices[0].message.content)

async def async_openai_stream(messages: List, model="gpt-4o-mini", temp=1, max_tokens=1024):
    response = await async_openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stream=True
    )
    return response