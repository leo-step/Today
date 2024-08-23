
from dotenv import load_dotenv
from retrievers import retrieve_crawl, retrieve_emails
from enum import Enum
from utils import with_timing, openai_json_response
from prompts import user_query, tool_and_rewrite

load_dotenv()

class Tool(Enum):
    CRAWL = "crawl"
    EMAILS = "emails"
    NONE = None

def document_to_str(document):
    return document["text"]

def format_documents(documents):
    texts = [document_to_str(doc) for doc in documents]
    return "\n\n".join(texts)

@with_timing
def invoke_tool(tool: Tool, tool_input: str):
    if tool == Tool.NONE:
        return ""
    elif tool == Tool.EMAILS:
        documents = retrieve_emails(tool_input)
        return format_documents(documents)
    else:
        documents = retrieve_crawl(tool_input)
        return format_documents(documents)
    
@with_timing
def choose_tool_and_rewrite(memory, query_text):
    response = openai_json_response([
        tool_and_rewrite(memory, query_text),
        user_query(query_text),
    ])
    tool: Tool = response["tool"]
    return tool, query_text
