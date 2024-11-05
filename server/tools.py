from retrievers import retrieve_crawl, retrieve_emails, retrieve_any, \
    retrieve_any_emails, retrieve_widget_data, retrieve_location_data, \
    retrieve_princeton_courses, retrieve_eating_clubs, retrieve_nearby_places
from utils import with_timing, openai_json_response
from prompts import user_query, tool_and_rewrite
from models import Tool, Tools
# import time
import json
from enum import Enum
import re

# def get_days_ago(past_time: int):
#     current_time = time.time()
#     current_day = int(current_time // 86400)
#     given_day = int(past_time // 86400)
#     days_diff = current_day - given_day

#     if days_diff == 0:
#         return "today"
#     elif days_diff == 1:
#         return "1 day ago"
#     else:
#         return f"{days_diff} days ago"

def document_to_str(document):
    text = document["text"]
    subject = text.split("\n")[0] if text.startswith("SUBJECT:") else ""
    body = "\n".join(text.split("\n")[1:]) if subject else text
    links = '\n'.join(document["links"])
    # days_ago = get_days_ago(document["time"])
    # scores = "vs:{}, fts:{}, score:{}".format(document["vs_score"], document["fts_score"], document["score"])
    # return "{}\n{}\n{}".format(text, links, days_ago)
    return f"{subject}\n\n{body}\n{links}"

def format_documents(documents):
    texts = [document_to_str(doc) for doc in documents]
    return "\n\n".join(texts)

def clean_query(query):
    # Lowercase the query for uniformity
    query = query.lower()
    # Remove common phrases
    common_phrases = [
        r'\blocation of\b',
        r'\bfind\b',
        r'\bin princeton\b',
        r'\bnear me\b',
        r'\bnearby\b',
        r'\baround here\b',
        r'\baround\b',
        r'\bwhat is\b',
        r'\bwhere is\b',
        r'\bhow close is\b',
        r'\bhow far is\b',
        r'\bis there a\b',
        r'\bnear\b',
        r'\bthe\b',
        r'\baddress of\b',
        r'\blocation\b',
        r'\bof\b',
        r'\bin\b'
    ]
    # Remove common phrases using regex
    for phrase in common_phrases:
        query = re.sub(phrase, '', query)
    # Remove any extra whitespace
    query = query.strip()
    # Return the cleaned query
    return query

def get_next_event_string(place):
    next_event = place.get('next_event')
    if not next_event:
        return ''
    # Format the event time
    event_time = next_event['time'].strftime('%A at %I:%M %p')
    if next_event['type'] == 'open':
        return f"\nOpens next on {event_time}"
    else:
        return f"\nCloses at {event_time}"

def format_place_response(place):
    response_parts = []

    # Basic information
    response_parts.append(f"{place['name']} is located at {place['address']}.")

    # Rating
    if place['rating'] != 'N/A':
        response_parts.append(f"It has a rating of {place['rating']} based on {place['user_ratings_total']} reviews.")

    # Current status
    if place['is_open_now'] is not None:
        status = "open" if place['is_open_now'] else "closed"
        response_parts.append(f"It's currently {status}.")

    # Next event (opening or closing time)
    if place.get('next_event'):
        event = place['next_event']
        event_time = event['time'].strftime('%A at %I:%M %p').lstrip('0')
        if event['type'] == 'open':
            response_parts.append(f"It will open next on {event_time}.")
        else:
            response_parts.append(f"It will close at {event_time}.")

    # Contact information
    contact_info = []
    if place['phone_number'] != 'N/A':
        contact_info.append(f"Phone number: {place['phone_number']}")
    if place['website'] != 'N/A':
        contact_info.append(f"Website: {place['website']}")

    if contact_info:
        response_parts.append("For more information, " + " or ".join(contact_info) + ".")

    # Combine the parts into a single response
    return " ".join(response_parts)

@with_timing
def invoke_tool(tool: str, tool_input: str) -> str:
    print("[INFO]", tool)
    if tool == Tool.EMAILS.value:
        documents = retrieve_emails(tool_input)
        return format_documents(documents)
    # elif tool == Tool.ALL_EMAILS.value:
    #     documents = retrieve_any_emails(tool_input)
    #     return format_documents(documents)
    elif tool == Tool.WIDGET_DATA.value:
        widget_data = retrieve_widget_data()
        return json.dumps(widget_data)
    elif tool == Tool.LOCATION.value:
        documents = retrieve_location_data(tool_input)
        texts = [doc["text"] for doc in documents]
        return "\n\n".join(texts)
    elif tool == Tool.COURSES.value:
        result = retrieve_princeton_courses(tool_input)
        if not result["main_course"]:
            return "Search results didn't return any courses."
            
        if result["is_current"]:
            # For comparison queries, include full details of other courses
            if len(result["other_courses"]) > 0 and isinstance(result["other_courses"][0], dict):
                return f"""***IMPORTANT: you must return this link to the user if you use this information - {result["url"]}***
                
                Main course:
                {json.dumps(result["main_course"])}

                Other relevant courses:
                {json.dumps(result["other_courses"])}"""
            else:
                # For regular queries, just return main course and other course codes
                return f"""***IMPORTANT: you must return this link to the user if you use this information - {result["url"]}***
                
                {json.dumps(result["main_course"])}

                Other related courses:
                """ + '\n'.join([f"{c['department']} {c['catalogNumber']}: {c['title']}" for c in result["other_courses"]])
        
        return f"""***[WARNING]: This class happened in a past semester.
        Please note that to the user so they are not confused. Also,
        everything you say should be in past tense!***

        ***IMPORTANT: you must return this link to the user if you use this information - {result["url"]}***

        {json.dumps(result["main_course"])}

        Other related courses:
        """ + '\n'.join([f"{c['department']} {c['catalogNumber']}: {c['title']}" for c in result["other_courses"]])
    elif tool == Tool.EATING_CLUBS.value:
        documents = retrieve_eating_clubs(tool_input)
        return format_documents(documents)
    elif tool == Tool.CATCHALL.value:
        documents = retrieve_any_emails(tool_input)
        return format_documents(documents)
    elif tool == Tool.NEARBY_PLACES.value:
        # Clean the tool_input to extract the main keyword
        keyword = clean_query(tool_input)
        print(f"[INFO] Cleaned keyword: '{keyword}'")
        # Check if keyword is empty after cleaning
        if not keyword:
            return "I'm sorry, I couldn't find any places matching your query."
        places = retrieve_nearby_places(keyword)
        if not places:
            return "I'm sorry, I couldn't find any places matching your query."
        # Generate a conversational response
        responses = [format_place_response(place) for place in places]
        final_response = "\n\n".join(responses)
        return final_response
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

class Tool(Enum):
    CRAWL = 'crawl'  # added missing tool
    EMAILS = 'emails'
    # ALL_EMAILS = 'all_emails'
    EATING_CLUBS = 'eating_clubs'
    WIDGET_DATA = 'widget_data'
    LOCATION = 'location'
    COURSES = 'courses'
    NEARBY_PLACES = 'nearby_places'
    CATCHALL = 'catchall'

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
            communication. Pay special attention to the email subject lines, 
            as they often contain crucial information, especially for brief
            announcements or events.
            ***IMPORTANT: you must use this tool when prompted
            about club related things that are coming up in the future because 
            all real-time club information is here! Note that past / expired
            events should not be accessed here***
            
            Not useful for answering questions about academic facts, classes,
            professors, and other general public university information.
        """
    },
    # {
    #     "name": Tool.ALL_EMAILS,
    #     "description": """This tool accesses all past Princeton listserv emails
    #         emails. Useful when you need to answer question about club and campus
    #         life events that may or may not have happened already. 
    #         ***IMPORTANT: you must use this tool when prompted about club related 
    #         things that can be general questions or questions about events that
    #         happened in the past. Don't refer to this tool for current or future
    #         events or club information.***
            
    #         Not useful for answering questions about academic facts, classes,
    #         professors, and other general public university information.
    #     """
    # },
    {
        "name": Tool.EATING_CLUBS,
        "description": f"""This tool accesses information about eating clubs, which 
        are different from regular clubs. The eating clubs are Tower Club (Tower), 
        Cannon Dial Elm Club (Cannon), Cap and Gown Club (Cap), Charter Club (Charter), 
        Cloister Inn (Cloist), Colonial Club (Colo), Cottage Club (Cottage), Ivy Club 
        (Ivy), Quadrangle Club (Quad), Terrace Club (Terrace), and Tiger Inn (TI).
        Some common phrases that are meant to refer to the eating clubs involve saying 
        the word 'street' or by asking what clubs are 'open'. Use this tool when asked
        about eating club information or anything relating to ***bicker***. A reference
        to the word ***street*** should also always invoke this tool!***
        
        ***IMPORTANT: if the user is asking about eating club events that happened in
        the past, you should use the {Tool.CATCHALL} tool. This tool will only access
        the upcoming events or general eating club information.***"""
    },
    {
        "name": Tool.WIDGET_DATA,
        "description": """This tool retrieves the current dining hall menus,
        weather data for Princeton, and a couple recent news articles from 
        the Daily Princetonian newspaper."""
    },
    {
        "name": Tool.LOCATION,
        "description": """This tool lets you find simple location information.
        It contains directories of cafes, sports fields, libraries, academic departments,
        residential colleges, and other physical locations. These locations
        have simple data associated with them, such as a phone number and the
        building they are in. Some contain other descriptions, such as what
        sports team plays on the field or what food in general is sold at the
        cafe. Useful for simple location queries such as naming the locations
        of a specific type and seeing where they are at. Not useful for
        detailed descriptions."""   
    },
    {
        "name": Tool.COURSES,
        "description": """This tool provides comprehensive course information and analysis:

        1. Course Information:
        - Direct course code lookup (e.g., "MAT201", "COS226")
        - Course descriptions, prerequisites, and requirements
        - Distribution requirements and assignments
        - Course evaluations and student feedback

        2. Course Reviews & Opinions:
        - Student evaluations and ratings
        - Detailed student comments and feedback
        - Overall course quality scores
        - Historical course data and trends

        3. Course Comparisons:
        - Compare multiple courses by difficulty, workload, content
        - Compare teaching styles and approaches
        - Compare distribution requirements and prerequisites
        - Analyze student experiences across courses

        4. Course Selection Help:
        - Find courses by specific criteria (e.g., "psets not papers")
        - Get advice on course combinations
        - Find courses that fulfill specific requirements
        - Get tips for success in specific courses

        ***IMPORTANT NOTES:***
        - Can answer questions like:
          * "What do people think about MAT201?"
          * "Compare COS217 and COS226 difficulties"
          * "Tips for success in COS217"
          * "What's the workload like in COS217?"
          * "What are good classes that have psets and not papers?"
        - Results include links to Princeton Courses for verification
        - Provides comprehensive analysis using course evaluations, comments, and ratings
        """
    },
    {
        "name": Tool.NEARBY_PLACES,
        "description": """This tool accesses the Google Places API to find specific places or businesses near Princeton University.
        Use this tool when the user asks about the location of a specific restaurant, store, or point of interest.
        It provides accurate and current information, including name, address, and ratings.
        
        **Use this tool for queries like:**
        - "Where is Starbucks?"
        - "Is there a Maruichi nearby?"
        - "Find the nearest bookstore."
        - "Where can I get boba?"
        """,
        "examples": """
        - **User Query**: "Where is Lan Ramen?"
          **Tool Input**: "Lan Ramen"
        - **User Query**: "Is there a Junbi nearby?"
          **Tool Input**: "Junbi"
        - **User Query**: "Find Starbucks near me."
          **Tool Input**: "Starbucks"
        - **User Query**: "Can I get boba nearby?"
          **Tool Input**: "Boba"
        """
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
