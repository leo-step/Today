from utils import get_embedding, openai_json_response, delete_dict_key_recursively, system_prompt, build_search_query
from clients import db_client
from prompts import extract_email_search_terms, email_search_query
import time
import requests
import os
import random
import re
import datetime
from dateutil import tz
import json

# time constants
HOURS_PER_DAY = 24
SECONDS_PER_HOUR = 3600

# search scoring weights
SUBJECT_MATCH_SCORE = 10
BODY_MATCH_SCORE = 5

# constants for embedding
PROCESSED_RESULTS_GENERIC = 25
PROCESSED_RESULTS_SPECIFIC = 15

@system_prompt
def get_course_search_prompt():
    return """You will receive a piece of text related to looking up a college course at Princeton, and you need to 
    extract the key search terms. Here are examples:
    
    Example 1 - Direct Course Code:
    Input: "should I take COS217"
    Output: "COS 217"

    Example 2 - Course Comparison:
    Input: "is COS217 harder than COS226"
    Output: "COS 217"  # Will look up first course, then compare

    Example 3 - Similar Course Query:
    Input: "what courses are similar to MAT201"
    Output: "MAT 201"  # Will find similar courses based on this

    Example 4 - Department Search:
    Input: "easy math classes"
    Output: "MAT"  # Department code for broad search

    Example 5 - Topic Search:
    Input: "artificial intelligence courses"
    Output: "artificial intelligence"

    Example 6 - Workload Query:
    Input: "what are the best no pset classes"
    Output: "no problem sets"  # Will search descriptions and comments

    Example 7 - Difficulty Query:
    Input: "what's an easy science requirement"
    Output: "science requirement easy"

    ***IMPORTANT RULES:***
    1. For course codes: Always include space between department and number (e.g., "COS 217" not "COS217")
    2. For department searches: Use official department codes (e.g., "MAT" for Mathematics)
    3. For topic searches: Use minimal keywords without words like "course" or "class"
    4. For workload queries: Include terms like "no problem sets", "no psets", "light workload"
    5. For difficulty queries: Include difficulty level (easy/hard) with requirements
    6. Never add words like "undergraduate" or "Princeton"

    Return a JSON where your output is a string under the key "search_query". For example:
    {
        "search_query": "COS 217"
    }
    """

def setup_mongodb_indices():
    collection = db_client["crawl"]
    
    # index for time and source
    collection.create_index([
        ("source", 1),
        ("time", -1)
    ], name="source_time_idx")
    
    # text index for subject and text fields
    collection.create_index([
        ("subject", "text"),
        ("text", "text")
    ], name="email_text_idx")
    
    print("MongoDB indices created successfully")
    
setup_mongodb_indices()

def retrieve_widget_data():
    collection = db_client["widgets"]
    return collection.find_one({"_id": "data"})

def retrieve_location_data(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text, "map")

def retrieve_crawl(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text, "web")

def retrieve_any(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text)

def process_email_doc(doc, current_time, score=1):
    """Process a single email document into the standard format"""
    age_hours = (current_time - doc.get("time", 0)) / SECONDS_PER_HOUR
    
    return {
        "_id": doc["_id"],
        "text": doc["text"],
        "subject": doc.get("subject", ""),
        "links": doc.get("links", []),
        "metadata": {
            "time": doc.get("time", 0),
            "source": doc.get("source", "email")
        },
        "score": score,
        "time_context": f"[{int(age_hours)} hours ago]"
    }

def get_time_filter(time_context, current_time):
    """Determine time filter based on GPT-determined time context"""
    if time_context == "current":
        return lambda doc: (current_time - (doc.get("metadata", {}).get("time", 0))) < 12 * SECONDS_PER_HOUR
    elif time_context == "past":
        return lambda doc: (current_time - (doc.get("metadata", {}).get("time", 0))) < 7 * HOURS_PER_DAY * SECONDS_PER_HOUR
    else:  # default
        return lambda doc: (current_time - (doc.get("metadata", {}).get("time", 0))) < 14 * HOURS_PER_DAY * SECONDS_PER_HOUR

def score_document(doc, search_terms):
    """Score a document based on search term matches"""
    score = 0
    for term in search_terms:
        if re.search(term, doc.get("subject", ""), re.IGNORECASE):
            score += SUBJECT_MATCH_SCORE # higher score for subject match
        if re.search(term, doc.get("text", ""), re.IGNORECASE):
            score += BODY_MATCH_SCORE # higher score for body match
    return score

def retrieve_emails(query_text):
    collection = db_client["crawl"]
    current_time = int(time.time())
    
    # extract search terms and time context using prompt
    search_info = openai_json_response([
        extract_email_search_terms(),
        email_search_query(query_text)
    ])
    
    search_terms = search_info["terms"]
    time_context = search_info.get("time_context", "default")
    print(f"[DEBUG] Search terms: {search_terms}")
    print(f"[DEBUG] Time context: {time_context}")

    # return recent emails if no search terms
    if not search_terms:
        base_query = {
            "$and": [
                {"source": "email"},
                {"time": {"$gt": current_time - (7 * HOURS_PER_DAY * SECONDS_PER_HOUR)}}
            ]
        }
        results = list(collection.find(base_query))
        processed_results = [process_email_doc(doc, current_time) for doc in results]
        processed_results.sort(key=lambda x: -(x.get("metadata", {}).get("time", 0)))
        return processed_results[:PROCESSED_RESULTS_GENERIC]

    # build search query using single regex with OR
    combined_pattern = "|".join(re.escape(term) for term in search_terms)
    base_query = {
        "$and": [
            {"source": "email"},
            {
                "$or": [
                    {"subject": {"$regex": f".*({combined_pattern}).*", "$options": "i"}},
                    {"text": {"$regex": f".*({combined_pattern}).*", "$options": "i"}}
                ]
            }
        ]
    }
    
    # try exact matches
    exact_matches = list(collection.find(base_query))
    
    # try fuzzy search if no exact matches
    if not exact_matches:
        print("[DEBUG] No exact matches, trying fuzzy search")
        fuzzy_conditions = []
        for term in search_terms:
            word_conditions = [{
                "$or": [
                    {"subject": {"$regex": f".*{re.escape(word)}.*", "$options": "i"}},
                    {"text": {"$regex": f".*{re.escape(word)}.*", "$options": "i"}}
                ]
            } for word in term.split()]
            fuzzy_conditions.append({"$and": word_conditions})
        
        base_query["$or"] = fuzzy_conditions
        exact_matches = list(collection.find(base_query))
    
    print(f"[DEBUG] Found {len(exact_matches)} matching documents")
    
    # process and score results
    processed_results = []
    for doc in exact_matches:
        score = score_document(doc, search_terms)
        if score > 0:
            processed_results.append(process_email_doc(doc, current_time, score))
    
    # sort by score and recency
    processed_results.sort(key=lambda x: (x.get("score", 0), -x.get("metadata", {}).get("time", 0)), reverse=True)
    
    # get timeframe from gpt
    time_filter = get_time_filter(time_context, current_time)
    processed_results = list(filter(time_filter, processed_results))
    
    return processed_results[:PROCESSED_RESULTS_SPECIFIC]

def retrieve_any_emails(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text, "email")

def retrieve_eating_clubs(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text, "eatingclub", expiry=True)

def retrieve_princeton_courses(query_text):
    """Enhanced course retrieval with semantic search"""
    collection = db_client["courses"]
    
    # extract course codes if present
    course_codes = re.findall(r'([A-Z]{3})\s*(\d{3}[A-Z]?)', query_text.upper())
    
    # check query type
    is_comparison = len(course_codes) > 1
    is_similarity = "similar" in query_text.lower() or "like" in query_text.lower()
    is_difficulty = any(word in query_text.lower() for word in 
        ["hard", "easy", "difficult", "challenging", "tough", "simple"])
    is_workload = any(word in query_text.lower() for word in
        ["pset", "problem set", "workload", "work", "assignment", "homework"])

    try:
        if is_comparison:
            # handle course comparison
            dept1, num1 = course_codes[0]
            dept2, num2 = course_codes[1]
            
            # get both courses with their evaluations
            pipeline = [
                {
                    "$match": {
                        "$or": [
                            {"department": dept1, "catalogNumber": num1},
                            {"department": dept2, "catalogNumber": num2}
                        ]
                    }
                }
            ]
            
            results = list(collection.aggregate(pipeline))
            if len(results) != 2:
                return {}, [], None, True
            
            # map results by department and catalog number
            courses = {f"{c['department']}{c['catalogNumber']}": c for c in results}
            course1 = courses.get(f"{dept1}{num1}")
            course2 = courses.get(f"{dept2}{num2}")
            
            # return the first course with comparison data
            course = course1
            course["comparison"] = {
                "other_course": f"{dept2} {num2}",
                "this_course_score": course1.get("scores", {}).get("Quality of Course"),
                "other_course_score": course2.get("scores", {}).get("Quality of Course")
            }
            
            other_results = [f"{dept2} {num2}: {course2.get('title', '')}"]
        
        elif is_workload or is_difficulty:
            # search for courses based on workload/difficulty
            pipeline = [
                {
                    "$match": {
                        "$or": [
                            # Match course code if provided
                            *({"department": dept, "catalogNumber": num} 
                              for dept, num in course_codes),
                            # Otherwise match description/comments
                            {"text": {"$regex": "(no (problem )?sets?|light workload|minimal work|easy|manageable)", "$options": "i"}}
                            if not course_codes else {}
                        ]
                    }
                },
                {
                    "$addFields": {
                        "quality_score": {"$ifNull": ["$scores.Quality of Course", 0]}
                    }
                },
                {
                    "$sort": {
                        "quality_score": -1
                    }
                },
                {
                    "$limit": 10
                }
            ]
            
            results = list(collection.aggregate(pipeline))
            if not results:
                return {}, [], None, True
            
            course = results[0]
            other_results = [
                f"{c['department']} {c['catalogNumber']}: {c['title']}"
                for c in results[1:5]
            ]
            
            # extract relevant comments
            if "text" in course:
                comments = []
                for line in course["text"].split("\n"):
                    if any(term in line.lower() for term in 
                          ["problem set", "pset", "workload", "work", "assignment",
                           "hard", "easy", "difficult", "challenging", "tough", "simple"]):
                        comments.append(line.strip())
                
                if comments:
                    course["difficulty_analysis"] = {
                        "scores": {
                            "Quality of Course": course.get("scores", {}).get("Quality of Course"),
                            "Quality of Written Assignments": course.get("scores", {}).get("Quality of Written Assignments")
                        },
                        "relevant_comments": comments[:3]
                    }
        
        else:
            # stsandard course search
            pipeline = [
                {
                    "$match": {
                        "$or": [
                            # Match course code if provided
                            *({"department": dept, "catalogNumber": num} 
                              for dept, num in course_codes),
                            # Otherwise match title/description
                            {"$text": {"$search": query_text}}
                            if not course_codes else {}
                        ]
                    }
                },
                {
                    "$addFields": {
                        "quality_score": {"$ifNull": ["$scores.Quality of Course", 0]}
                    }
                },
                {
                    "$sort": {
                        "quality_score": -1
                    }
                },
                {
                    "$limit": 10
                }
            ]
            
            results = list(collection.aggregate(pipeline))
            if not results:
                return {}, [], None, True
            
            course = results[0]
            other_results = [
                f"{c['department']} {c['catalogNumber']}: {c['title']}"
                for c in results[1:5]
            ]

        # clean up course object
        course = {k:v for k,v in course.items() if k not in ['_id', 'embedding']}
        
        # convert _id to string for URL
        course_id = str(course.get('courseID', ''))
        link = f"https://www.princetoncourses.com/course/{course_id}"
        
        return course, other_results, link, True

    except Exception as e:
        print("[ERROR] Course retrieval failed:", e)
        return {}, [], None, True

def retrieve_nearby_places(query_text):
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY not set in environment variables")

    # exact coords of prospect house bc imo it's the most central point on campus
    location = {
        'latitude': 40.34711483385821,
        'longitude': -74.65678397916251
    }

    # endpoint for nearby search
    endpoint_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

    # prep parameters
    params = {
        'location': f"{location['latitude']},{location['longitude']}",
        'radius': 7000,  # metres; increased radius to 7km
        'keyword': query_text,
        'key': api_key,
        'type': 'establishment',  # optional: limits results to businesses; it's worked pretty well in testing
    }

    response = requests.get(endpoint_url, params=params)

    try:
        data = response.json()
    except ValueError:
        raise Exception(f"Error parsing JSON response: {response.text}")

    if response.status_code != 200 or data.get('status') not in ['OK', 'ZERO_RESULTS']:
        error_message = data.get('error_message', 'Unknown error')
        raise Exception(f"Error fetching data from Google Places API: {error_message}")

    places = []
    results = data.get('results', [])
    for result in results:
        # only retrieve details for first result to stop excess usage
        if len(places) >= 5:
            break

        # make a place details API call to get website/phone #
        place_id = result.get('place_id')
        details = {}
        if place_id:
            details = get_place_details(place_id, api_key)

        place_info = {
            'name': result.get('name', ''),
            'address': result.get('vicinity', ''),
            'types': result.get('types', []),
            'rating': result.get('rating', 'N/A'),
            'user_ratings_total': result.get('user_ratings_total', 0),
            'opening_hours': details.get('opening_hours', {}).get('weekday_text', []),
            'is_open_now': details.get('opening_hours', {}).get('open_now'),
            'business_status': result.get('business_status', 'N/A'),
            'website': details.get('website', 'N/A'),
            'phone_number': details.get('formatted_phone_number', 'N/A'),
            'next_event': details.get('next_event', None)
        }
        places.append(place_info)

    return places

def get_place_details(place_id, api_key):
    # endpoint for place details
    details_url = 'https://maps.googleapis.com/maps/api/place/details/json'

    # prep parameters
    params = {
        'place_id': place_id,
        'fields': 'website,formatted_phone_number,opening_hours',
        'key': api_key
    }

    # make GET request
    response = requests.get(details_url, params=params)

    # check if response is JSON
    try:
        data = response.json()
    except ValueError:
        return {}

    if response.status_code != 200 or data.get('status') != 'OK':
        return {}

    # extract desired fields
    result = data.get('result', {})
    details = {
        'website': result.get('website', 'N/A'),
        'formatted_phone_number': result.get('formatted_phone_number', 'N/A'),
        'opening_hours': result.get('opening_hours', {})
    }

    # add logic to compute next open or close time
    details['next_event'] = get_next_event(details['opening_hours'])

    return details

def get_next_event(opening_hours):
    if not opening_hours:
        return None

    periods = opening_hours.get('periods', [])
    if not periods:
        return None

    # get current time in EST
    now = datetime.datetime.now(tz=tz.gettz('America/New_York'))
    time_now = int(now.strftime('%H%M'))  # current time in HHMM format
    current_day = now.weekday()

    # Google API days: sunday is 0, monday is 1, ..., saturday is 6
    google_day = (current_day + 1) % 7

    upcoming_events = []

    for day_offset in range(7):
        day = (google_day + day_offset) % 7
        event_date = now.date() + datetime.timedelta(days=day_offset)

        for period in periods:
            if period['open']['day'] == day:
                open_time = int(period['open']['time'])
                # check if 'close' exists in period
                if 'close' in period:
                    close_time = int(period['close']['time'])
                else:
                    # handle places that are open 24 hours
                    close_time = open_time + 2400  # assumes place is open for 24 hours

                # if store closes after midnight
                if close_time < open_time:
                    close_time += 2400  # adjust close time for next day

                if day_offset == 0:
                    # today
                    if time_now < open_time:
                        # store will open later today
                        event_time = datetime.datetime.combine(
                            event_date,
                            datetime.datetime.strptime(str(open_time).zfill(4), '%H%M').time(),
                            tzinfo=now.tzinfo
                        )
                        upcoming_events.append({'type': 'open', 'time': event_time})
                    elif time_now < close_time:
                        # store is currently open and will close later today
                        event_time = datetime.datetime.combine(
                            event_date,
                            datetime.datetime.strptime(str(close_time % 2400).zfill(4), '%H%M').time(),
                            tzinfo=now.tzinfo
                        )
                        upcoming_events.append({'type': 'close', 'time': event_time})
                else:
                    # future days
                    event_time = datetime.datetime.combine(
                        event_date,
                        datetime.datetime.strptime(str(open_time).zfill(4), '%H%M').time(),
                        tzinfo=now.tzinfo
                    )
                    upcoming_events.append({'type': 'open', 'time': event_time})

    # sort events by time
    upcoming_events.sort(key=lambda x: x['time'])

    for event in upcoming_events:
        if event['time'] > now:
            return event

    return None

def hybrid_search(collection, query, source=None, expiry=False, sort=None, max_results=10):
    query_vector = get_embedding(query)

    vector_pipeline = [
        {
            "$vectorSearch":
                {
                    "queryVector": query_vector,
                    "path": "embedding",
                    "numCandidates": 100,
                    "limit": 10,
                    "index": "vector_index"
                },
        },
        {
            "$project": 
                {
                    "_id": 1,
                    "text": 1,
                    "links": 1,
                    "time": 1,
                    "score":{"$meta":"vectorSearchScore"}
                }
        }
    ]

    current_time = int(time.time())

    if source and expiry:
        vector_pipeline[0]["$vectorSearch"]["filter"] = {
            "$and": [
                {
                    "source": {
                        "$eq": source
                    }
                },
                {
                    "expiry": {
                        "$gt": current_time
                    }
                }
            ]
        }
    elif source:
        vector_pipeline[0]["$vectorSearch"]["filter"] = {
            "source": {
                "$eq": source
            }
        }

    vector_results = collection.aggregate(vector_pipeline)
    x = list(vector_results)
    
    keyword_pipeline = [
        {
            "$search": {
                "index": "full-text-search",
                "text": {
                    "query": query,
                    "path": "text"
                }
            }
        },
        { "$addFields" : { "score": { "$meta": "searchScore" } } },
        { "$limit": 5 }
    ]

    if source and expiry: 
        keyword_pipeline.insert(1, {
            "$match": {
                    "source": source,
                    "expiry": { "$gt": current_time }
                }
            })
    elif source:
        keyword_pipeline.insert(1, {
            "$match": {
                "source": source
            }
        })

    keyword_results = collection.aggregate(keyword_pipeline)
    y = list(keyword_results)
    
    doc_lists = [x,y]

    for i in range(len(doc_lists)):
        doc_lists[i] = [
            {"_id":str(doc["_id"]), "text":doc["text"], 
             "links":doc["links"], "time":doc["time"], 
             "score": doc["score"]}
            for doc in doc_lists[i]
        ]
    
    fused_documents = weighted_reciprocal_rank(doc_lists)

    return fused_documents[:max_results]

def weighted_reciprocal_rank(doc_lists):
    """
    This is a modified version of the fuction in the langchain repo
    https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/retrievers/ensemble.py
    
    Perform weighted Reciprocal Rank Fusion on multiple rank lists.
    You can find more details about RRF here:
    https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf

    Args:
        doc_lists: A list of rank lists, where each rank list contains unique items.

    Returns:
        list: The final aggregated list of items sorted by their weighted RRF
                scores in descending order.
    """
    c=60 #c comes from the paper
    weights=[1]*len(doc_lists) #you can apply weights if you like, here they are all the same, ie 1
    
    if len(doc_lists) != len(weights):
        raise ValueError(
            "Number of rank lists must be equal to the number of weights."
        )

    # Create a union of all unique documents in the input doc_lists
    all_documents = set()
    for doc_list in doc_lists:
        for doc in doc_list:
            all_documents.add(doc["text"])

    # Initialize the RRF score dictionary for each document
    rrf_score_dic = {doc: 0.0 for doc in all_documents}

    # Calculate RRF scores for each document
    for doc_list, weight in zip(doc_lists, weights):
        for rank, doc in enumerate(doc_list, start=1):
            rrf_score = weight * (1 / (rank + c))
            rrf_score_dic[doc["text"]] += rrf_score

    # Sort documents by their RRF scores in descending order
    sorted_documents = sorted(
        rrf_score_dic.keys(), key=lambda x: rrf_score_dic[x], reverse=True
    )

    # Map the sorted page_content back to the original document objects
    page_content_to_doc_map = {
        doc["text"]: doc for doc_list in doc_lists for doc in doc_list
    }
    sorted_docs = [
        page_content_to_doc_map[page_content] for page_content in sorted_documents
    ]

    return sorted_docs
