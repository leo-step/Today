from clients import openai_client, async_openai_client
from dotenv import load_dotenv
from typing import List
import time
import os
import json
from datetime import datetime
from pytz import timezone

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

def time_to_date_string():
    # Define the New York timezone
    ny_timezone = timezone('America/New_York')

    # Get the current time in New York
    current_time_ny = datetime.now(ny_timezone)

    # Format the current time as a string
    return current_time_ny.strftime("%A, %B %d, %Y %I:%M %p")

def delete_dict_key_recursively(data, del_key):
    if isinstance(data, dict):
        if del_key in data:
            del data[del_key]
        for key in data:
            data[key] = delete_dict_key_recursively(data[key], del_key)
    elif isinstance(data, list):
        data = [delete_dict_key_recursively(item, del_key) for item in data]
    return data
