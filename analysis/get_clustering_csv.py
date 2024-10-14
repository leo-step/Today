import json
import pandas as pd
from clients import openai_client
from dotenv import load_dotenv
import concurrent.futures

load_dotenv()

clean_messages = []

with open("conversations_dump.json", "r") as fp:
    data = json.load(fp)
    for convo in data:
        ai_messages = list(filter(lambda x: x["type"] == "ai", convo["messages"]))
        for i, message in enumerate(ai_messages):
            if not message["tool_use"]["input"] or not message["tool_use"]["tool"]:
                continue
            clean = {
                "conversation_id": convo["_id"], 
                "ai_message_index": i, 
                "rewritten_query": message["tool_use"]["input"],
                "tool": message["tool_use"]["tool"]
            }
            clean_messages.append(clean)

def get_embedding(query_text, model="text-embedding-3-large", dimensions=256):
   query_text = query_text.replace("\n", " ")
   return openai_client.embeddings.create(input = [query_text], model=model, dimensions=dimensions).data[0].embedding

def add_embeddings(message):
    embedding = get_embedding(message["rewritten_query"])
    message["embedding"] = embedding
    return message

with concurrent.futures.ThreadPoolExecutor() as executor:
    clean_messages = list(executor.map(add_embeddings, clean_messages))

df = pd.DataFrame(clean_messages)
df.to_csv("clustering.csv")
