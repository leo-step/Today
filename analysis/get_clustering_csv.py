import json
import pandas as pd
from clients import openai_client
from dotenv import load_dotenv
import concurrent.futures
import replicate

load_dotenv()
client = replicate.Client(api_token='')
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

def add_embeddings(message):
    embedding = get_embedding(message["rewritten_query"], model="embeddings-gte-base", dimensions=32)
    message["embedding"] = embedding
    print("done")
    return message

with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    clean_messages = list(executor.map(add_embeddings, clean_messages))

df = pd.DataFrame(clean_messages)
df.to_csv("clustering_768.csv")
