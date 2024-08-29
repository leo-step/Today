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
def invoke_tool(tool: Tool | None, tool_input: str):
    if tool == None:
        print("[INFO] no tool used")
        return ""
    elif tool == Tool.EMAILS.value:
        documents = retrieve_emails(tool_input)
        return format_documents(documents)
    else:
        documents = retrieve_crawl(tool_input)
        return format_documents(documents)
    
@with_timing
def choose_tool_and_rewrite(tools, memory, query_text):
    response = openai_json_response([
        tool_and_rewrite(tools, memory),
        user_query(query_text),
    ])
    tool: Tool | None = response["tool"]
    query_rewrite = response["query_rewrite"]
    return tool, query_rewrite


# =========== TOOLS =========== #

tools: Tools = [
    {
        "name": Tool.CRAWL,
        "description": """This tool accesses a crawl of all Princeton
            and Princeton-related webpages. Useful when you need to answer
            questions about the university, academic requirements, professors,
            various academic programs, general information about campus life,
            and other general things that would be listed on a university 
            webpage, as well as recent university-wide news. You should
            use this tool for any professor related information.
            
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
            and things going on in campus life. This accesses information
            primary relating to student activities, not official university
            communication.
            
            Not useful for answering questions about academic facts, classes,
            professors, and other general public university information.
        """
    }
]
