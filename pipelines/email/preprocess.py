from dotenv import load_dotenv
import json
from openai import OpenAI
from datetime import datetime, timedelta
import pytz

load_dotenv()

openai_client = OpenAI()

def openai_json_response(messages, model="gpt-4o-mini", temp=1, max_tokens=1024):
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

def get_expiry_time(page_content):
    result = openai_json_response([{
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": f"""{page_content}\n\nReturn a JSON with key 'time' and value in the format MM-DD-YYYY 
                where the date is the latest date found in this email. Consider all the dates! It's important to find
                the latest date out of all of them, no matter the format. Today's date is Tuesday, September 10th, 
                2024, and you can use this fact to reason about any relative dates. If there is no date referenced,
                return null for the time."""
            }
        ]
    }])

    date_str = result['time']
    if date_str:
        ny_tz = pytz.timezone('America/New_York')
        date_obj = datetime.strptime(date_str, '%m-%d-%Y')
        ny_midnight = ny_tz.localize(date_obj)
        return int(ny_midnight.timestamp())
    else:
        current_time = datetime.now()
        one_week_from_now = current_time + timedelta(weeks=1)
        return int(one_week_from_now.timestamp())
