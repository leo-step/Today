from retrievers import retrieve_crawl, retrieve_emails
from utils import with_timing, openai_json_response
from prompts import user_query, tool_and_rewrite
from models import Tool, Tools

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
def choose_tool_and_rewrite(tools, memory, query_text):
    response = openai_json_response([
        tool_and_rewrite(tools, memory, query_text),
        user_query(query_text),
    ])
    tool: Tool = response["tool"]
    return tool, query_text


# =========== TOOLS =========== #

tools: Tools = [
    {
        "name": Tool.CRAWL,
        "description": """This tool accesses a crawl of all Princeton
            and Princeton-related webpages. Useful when you need to answer
            questions about the university, academic requirements, professors,
            various academic programs, general information about campus life,
            and other general things that would be listed on a university 
            webpage. 
            
            Not useful for answering questions that involve real time
            information about campus life, clubs, events, job opportunity 
            postings, and other similar kinds of information.

            Should be used as a default fallback when other tools don't 
            give a good response.
        """
    },
    {
        "name": Tool.EMAILS,
        "description": """This tool accesses the latest Princeton listserv
            emails. Useful when you need to answer question about real time
            events, clubs, job opportunity postings, deadlines for auditions,
            and things going on in campus life.
            
            Not useful for answering questions about academic facts, classes,
            professors, and other general public university information.
        """
    }
]
