from retrievers import retrieve_crawl, retrieve_emails, retrieve_any, retrieve_any_emails, retrieve_widget_data
from utils import with_timing, openai_json_response
from prompts import user_query, tool_and_rewrite
from models import Tool, Tools
import time

def get_days_ago(past_time: int):
    current_time = time.time()
    current_day = int(current_time // 86400)
    given_day = int(past_time // 86400)
    days_diff = current_day - given_day

    if days_diff == 0:
        return "today"
    elif days_diff == 1:
        return "1 day ago"
    else:
        return f"{days_diff} days ago"

def document_to_str(document):
    text = document["text"]
    links = '\n'.join(document["links"])
    days_ago = get_days_ago(document["time"])
    # scores = "vs:{}, fts:{}, score:{}".format(document["vs_score"], document["fts_score"], document["score"])
    return "{}\n{}\n{}".format(text, links, days_ago)

def format_documents(documents):
    texts = [document_to_str(doc) for doc in documents]
    return "\n\n".join(texts)

@with_timing
def invoke_tool(tool: Tool | None, tool_input: str):
    print("[INFO]", tool)
    if tool == None:
        print("[INFO] no tool used")
        return ""
    elif tool == Tool.EMAILS.value:
        documents = retrieve_emails(tool_input)
        return format_documents(documents)
    elif tool == Tool.ALL_EMAILS.value:
        documents = retrieve_any_emails(tool_input)
        return format_documents(documents)
    elif tool == Tool.WIDGET_DATA.value:
        widget_data = retrieve_widget_data()
        return str(widget_data)
    # TODO: eating club data, courses data, 
    # club/people data through google form (with approval)
    # ^^ interesting utility idea
    elif tool == Tool.CATCHALL.value:
        documents = retrieve_any(tool_input)
        return format_documents(documents)
    else:
        documents = retrieve_crawl(tool_input)
        return format_documents(documents)
    
@with_timing
def choose_tool_and_rewrite(tools, memory, query_text):
    response = openai_json_response([
        tool_and_rewrite(tools, memory),
        user_query(query_text),
    ], model="gpt-4o")
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
            communication. ***IMPORTANT: you must use this tool when prompted
            about club related things that are coming up in the future because 
            all real-time club information is here! Note that past / expired
            events should not be accessed here***
            
            Not useful for answering questions about academic facts, classes,
            professors, and other general public university information.
        """
    },
    {
        "name": Tool.ALL_EMAILS,
        "description": """This tool accesses all past Princeton listserv emails
            emails. Useful when you need to answer question about club and campus
            life events that may or may not have happened already. 
            ***IMPORTANT: you must use this tool when prompted about club related 
            things that can be general questions or questions about events that
            happened in the past. Don't refer to this tool for current or future
            events or club information.***
            
            Not useful for answering questions about academic facts, classes,
            professors, and other general public university information.
        """
    },
    {
        "name": Tool.WIDGET_DATA,
        "description": """This tool retrieves the current dining hall menus,
        weather data for Princeton, and a couple recent news articles from 
        the Daily Princetonian newspaper."""
    },
    {
        "name": Tool.CATCHALL,
        "description": """This tool serves as a catch-all where it searches
        across all data sources, including the web crawl and emails. This tool
        is meant to be used when the query contains a lot of acronyms or unfamilar
        language. For example, 'when is PUCP meeting?' should be directed to this
        tool because PUCP is an unknown acronym that needs to be searched for.
        Additionally, use this tool when prompted about club events that happened
        in the past."""
    }
]
