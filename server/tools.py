
from dotenv import load_dotenv
from retrievers import retrieve_crawl, retrieve_emails
from enum import Enum
from clients import openai_client
from utils import with_timing
import json

load_dotenv()

class Tool(Enum):
    CRAWL = "crawl"
    EMAILS = "emails"
    NONE = None

def document_to_str(document):
    return document["text"]

@with_timing
def invoke_tool(tool: Tool, tool_input: str):
    if tool == Tool.NONE:
        return ""
    elif tool == Tool.EMAILS:
        documents = retrieve_emails(tool_input)
        texts = [document_to_str(doc) for doc in documents]
        return "\n\n".join(texts)
    else:
        documents = retrieve_crawl(tool_input)
        texts = [document_to_str(doc) for doc in documents]
        return "\n\n".join(texts)
    
@with_timing
def choose_tool_and_rewrite(memory, query_text):
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": "Return a JSON in the format {\"tool\": \"tool_name\"} where tool_name is either \"Crawl\" \"Emails\" or null"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Return Crawl"
                    }
                ]
            },
        ],
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={
            "type": "json_object"
        }
    )

    tool: Tool = json.loads(response.choices[0].message.content)["tool"]

    return tool, query_text
