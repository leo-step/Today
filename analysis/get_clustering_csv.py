import json
import pandas as pd
from clients import openai_client
from dotenv import load_dotenv
import concurrent.futures
import replicate

load_dotenv()
client = replicate.Client(api_token='')
clean_messages = []

def system_prompt(func):
    def wrapper(*args, **kwargs):
        text = func(*args, **kwargs)
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

@system_prompt
def identify_issue():
    return '''Your job is to analyze chatbot conversations and identify places
    where the chatbot had issues answering the query. You will be given the AI response. You 
    should read the response and determine whether there was an issue. Some criteria for
    this are: failing to find the right documents, not finding an exact match to the subject,
    giving a hesitant or unsure or not enough information-type answer, etc. Use your best judgement. 
    Respond with a JSON with key "issue_detected" where the value is a boolean true if the AI had a problem
    with responding or false if there were no issues. You will now be given the text.'''

@user_prompt
def message_text(response: str):
    return f'''AI response: {response}'''

with open("conversations_dump.json", "r") as fp:
    data = json.load(fp)
    for convo in data:
        ai_messages = list(filter(lambda x: x["type"] == "ai", convo["messages"]))
        for i, message in enumerate(ai_messages):
            if not message["tool_use"]["input"] or not message["tool_use"]["tool"]:
                continue
            # flag issue = next question very similar to previous question (mehhh, hard to tell)
#               OR current response expresses unsure or doesn't answer question
            response = openai_json_response([
                identify_issue(),
                message_text(message["content"])
            ])
            issue_detected = response["issue_detected"]
            clean = {
                "conversation_id": convo["_id"], 
                "ai_message_index": i, 
                "rewritten_query": message["tool_use"]["input"],
                "tool": message["tool_use"]["tool"],
                "issue_detected": issue_detected,
                "response": message["content"]
            }
            print("done")
            clean_messages.append(clean)

def get_embedding(query_text, model="text-embedding-3-large", dimensions=256):
    query_text = query_text.replace("\n", " ")
    if model == "embeddings-gte-base":
        for _ in range(10):
            try:
                output = client.run(
                        "mark3labs/embeddings-gte-base:d619cff29338b9a37c3d06605042e1ff0594a8c3eff0175fd6967f5643fc4d47",
                        input={
                            "text": query_text
                        }
                    )
                return output["vectors"]
            except:
                print("retrying")
                continue
        raise Exception("failed all retries")
    return openai_client.embeddings.create(input = [query_text], model=model, dimensions=dimensions).data[0].embedding

# def add_embeddings(message):
#     embedding = get_embedding(message["rewritten_query"], dimensions=256)
#     message["embedding"] = embedding
#     return message

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     clean_messages = list(executor.map(add_embeddings, clean_messages))

df = pd.DataFrame(clean_messages)

# df["embedding"] = pd.read_csv("clustering_768.csv")["embedding"]

df.to_csv("clustering_1_768.csv")
