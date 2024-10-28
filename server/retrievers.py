from utils import get_embedding, openai_json_response, delete_dict_key_recursively
from clients import db_client
import time
import requests
from prompts import get_courses_search_query, user_query
import os
import random
import re
import datetime
from dateutil import tz
import json

def retrieve_widget_data():
    collection = db_client["widgets"]
    return collection.find_one({"_id": "data"})

def retrieve_location_data(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text, "map")

def retrieve_crawl(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text, "web")

def retrieve_emails(query_text):
    collection = db_client["crawl"]
    current_time = int(time.time())
    
    # extract important search terms
    search_info = openai_json_response([{
        "role": "system",
        "content": """Extract ONLY the specific items, topics, or subjects being asked about. 
        Ignore all helper words, time words, and generic terms like 'events', 'things', 'activities', 'announcements', etc.
        Never include terms like 'princeton', 'campus', 'today', 'tomorrow', 'yesterday', 'last', 'next', 'this', 'that', 'the', etc,
        as it can be assumed that all the emails retrieved will be related to Princeton University, and therefore those terms are irrelevant.
        **NEVER** make up any information or events, as it would be misleading students.
        Return a JSON with:
        - 'terms': array of ONLY the specific items/topics being searched for

        Examples:
        "is there any free pizza available right now?" -> {"terms": ["pizza", "freefood", "free pizza"]}
        "are there any israel/palestine related events right now? or soon?" -> {"terms": ["israel", "palestine"]}
        "what events are there about israel or palestine?" -> {"terms": ["israel", "palestine"]}
        "was there free fruit yesterday?" -> {"terms": ["fruit", "freefood", "free fruit"]}
        "when is the next narcan training session today?" -> {"terms": ["narcan", "training", "narcan training"]}
        "any fruit related events happening now?" -> {"terms": ["fruit"]}
        "were there any tacos and olives on campus?" -> {"terms": ["tacos", "olives"]}
        "is there anything about israel going on right now?" -> {"terms": ["israel"]}
        "was there any free food yesterday in the kanji lobby?" -> {"terms": ["food", "kanji lobby", "kanji"]}
        "are there any events about climate change tomorrow?" -> {"terms": ["climate", "climate change"]}
        "what's happening with SJP this week?" -> {"terms": ["sjp"]}
        "any fruit bowls available today?" -> {"terms": ["fruit", "fruit bowl", "freefood"]}
        "when is the next a cappella performance?" -> {"terms": ["cappella", "performance"]}
        "are there any dance shows this weekend?" -> {"terms": ["dance"]}
        "is there volleyball practice tonight?" -> {"terms": ["volleyball"]}
        "any meditation sessions happening soon?" -> {"terms": ["meditation"]}
        "where can I find free coffee right now?" -> {"terms": ["coffee", "freefood", "free coffee"]}
        "is the chess club meeting today?" -> {"terms": ["chess", "chess club"]}
        "any robotics workshops this week?" -> {"terms": ["robotics"]}
        "when's the next movie screening?" -> {"terms": ["movie", "screening"]}
        "are there any study groups for organic chemistry?" -> {"terms": ["chemistry", "organic"]}
        "is anyone giving away free textbooks?" -> {"terms": ["textbook", "free textbook"]}
        "what time is the math help session?" -> {"terms": ["math", "math help", "session"]}
        "what are the latest filipino events?" -> {"terms": ["filipino", "phillipines"]}
        "are there any events about palestine happening today?" -> {"terms": ["palestine"]}
        "what fruit events were there yesterday?" -> {"terms": ["fruit"]}
        Whenever a user has a query that is related to free food, you should always return "freefood" without a space between the words.    
        """
    }, {
        "role": "user",
        "content": query_text
    }])
    
    search_terms = search_info["terms"]
    print(f"[DEBUG] Search terms: {search_terms}")

    
    # if no search terms, return all emails from last month
    if not search_terms:
        base_query = {
            "$and": [
                {"source": "email"},
                {"time": {"$gt": current_time - (7 * 24 * 3600)}}  # change as needed
            ]
        }
        
        results = list(collection.find(base_query))
        processed_results = []
        
        for doc in results:
            age_hours = (current_time - doc.get("time", 0)) / 3600
            
            processed_doc = {
                "_id": doc["_id"],
                "text": doc["text"],
                "subject": doc.get("subject", ""),
                "links": doc.get("links", []),
                "metadata": {
                    "time": doc.get("time", 0),
                    "source": doc.get("source", "email")
                },
                "score": 1,  # default score
                "time_context": f"[{int(age_hours)} hours ago]"
            }
            processed_results.append(processed_doc)
        
        # sort by recency
        processed_results.sort(key=lambda x: -x["metadata"]["time"])
        return processed_results[:10]
    
    
    # build search conditions for each term
    search_conditions = []
    for term in search_terms:
        # create pattern that matches term
        term_pattern = f".*{re.escape(term)}.*"
        
        # search in both subject and body
        # regex is a pain
        term_conditions = {
            "$or": [
                {"subject": {"$regex": term_pattern, "$options": "i"}},
                {"text": {"$regex": term_pattern, "$options": "i"}}
            ]
        }
        search_conditions.append(term_conditions)
    
    # combine search conditions
    base_query = {
        "$and": [
            {"source": "email"},
            {"$or": search_conditions}
        ]
    }
    
    # first try exact matches
    exact_matches = list(collection.find(base_query))
    
    # if no results, try fuzzy searching
    # this code is not original,,, but it works so whatever
    if not exact_matches:
        print("[DEBUG] No exact matches, trying fuzzy search")
        fuzzy_conditions = []
        for term in search_terms:
            words = term.split()
            word_conditions = []
            for word in words:
                word_pattern = f".*{re.escape(word)}.*"
                word_conditions.append({
                    "$or": [
                        {"subject": {"$regex": word_pattern, "$options": "i"}},
                        {"text": {"$regex": word_pattern, "$options": "i"}}
                    ]
                })
            fuzzy_conditions.append({"$and": word_conditions})
        
        base_query["$or"] = fuzzy_conditions
        exact_matches = list(collection.find(base_query))
    
    print(f"[DEBUG] Found {len(exact_matches)} matching documents")
    
    # process and score results
    processed_results = []
    for doc in exact_matches:
        score = 0
        for term in search_terms:
            # higher score for subject matches
            if re.search(term, doc.get("subject", ""), re.IGNORECASE):
                score += 10
            # higher score for body matches
            if re.search(term, doc.get("text", ""), re.IGNORECASE):
                score += 5
        
        if score > 0:
            age_hours = (current_time - doc.get("time", 0)) / 3600
            
            processed_doc = {
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
            processed_results.append(processed_doc)
    
    # sort by score first then recency
    processed_results.sort(key=lambda x: (x["score"], -x["metadata"]["time"]), reverse=True)
    
    # now filter based on time context from original query
    is_current = any(word in query_text.lower() for word in [
        "now", "current", "today", "happening", "soon", "right now", "latest", "free food", "freefood", "recent"
    ])
    include_past = any(word in query_text.lower() for word in [
        "yesterday", "past", "previous", "before", "earlier", "last", ""
    ])
    
    # the following filters are arbitrarily chose, but these work pretty well
    # in my testing; feel free to change as necessary
    if is_current:
        # for current queries only show events from last 12h
        processed_results = [
            doc for doc in processed_results 
            if (current_time - doc["metadata"]["time"]) < 12 * 3600
        ]
    elif include_past:
        # for past queries show everything from last 7 days
        processed_results = [
            doc for doc in processed_results 
            if (current_time - doc["metadata"]["time"]) < 7 * 24 * 3600
        ]
    else:
        # default to last 2w
        processed_results = [
            doc for doc in processed_results 
            if (current_time - doc["metadata"]["time"]) < 24 * 3600 * 14
        ]
    
    return processed_results[:10]

def retrieve_any_emails(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text, "email")

def retrieve_eating_clubs(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text, "eatingclub", expiry=True)

def retrieve_princeton_courses(query_text):
    response = openai_json_response([
        get_courses_search_query(),
        user_query(query_text)
    ], model="gpt-4o")
    search_query = response["search_query"]
    replace_words = ["undergraduate", "Princeton", "class", "classes", "difficulty", "course", "courses"]
    for word in replace_words:
        search_query = search_query.replace(word, "")
    search_query = search_query.strip()
    print("[INFO] courses search query:", search_query)

    semester = int(os.getenv("SEMESTER"))
    headers = {
        "Authorization": "Bearer " + os.getenv("COURSES_API_KEY")
    }
    try:
        for i in range(8):
            print("[INFO] trying semester", semester)
            response = requests.get(f"https://www.princetoncourses.com/api/search/{search_query}?semester={semester}&sort=rating&detectClashes=false", headers=headers)
            try:
                search_results = response.json()
                if len(search_results) == 0:
                    if semester % 10 == 2:
                        semester -= 8
                    else:
                        semester -= 2
                    continue
                course_id = random.choice(search_results)["_id"]
                response = requests.get(f"https://www.princetoncourses.com/api/course/{course_id}", headers=headers)
                data = delete_dict_key_recursively(response.json(), "courses")
                data = delete_dict_key_recursively(data, "course")
                data = delete_dict_key_recursively(data, "_id")
                link = f"https://www.princetoncourses.com/course/{course_id}"
                other_search_results = []
                for search_result in search_results:
                    if search_result["_id"] == course_id:
                        continue
                    other_search_results.append("{} {}: {}".format(search_result["department"], 
                                        search_result["catalogNumber"], search_result["title"]))
                return data, other_search_results, link, i == 0
            except Exception as e:
                print("[ERROR] response 1 failed:", e)
                return {}, [], None, True
    except Exception as e:
        print("[ERROR] response 2 failed:", e)
    return {}, [], None, True

def retrieve_any(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text)

def hybrid_search(collection, query, source=None, expiry=False, sort=None, max_results=10):
    query_vector = get_embedding(query)

    vector_pipeline = [
        {
            "$vectorSearch":
                {
                    "queryVector": query_vector,
                    "path": "embedding",
                    "numCandidates": 50,
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
        # apparently there's 'fields' parameter for nearby search api; fields are predefined
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

# google api lowkey is a mess; im prolly overcomplicating it,
# but hardcoding location response formats is safer imo
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

def clean_query(query):
    # lowercase the query for uniformity
    query = query.lower()
    # remove common phrases
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
        r'\bnearest\b',
        r'\bthe\b',
        r'\baddress of\b',
        r'\blocation\b',
        r'\bof\b',
        r'\bin\b',
        r'\bto\b',
        r'\bprinceton\b',
        r'\buniversity\b',
        r'\bplease\b',
        r'\bcan you\b',
        r'\bcould you\b',
        r'\btell me\b',
        r'\?',
    ]
    for phrase in common_phrases:
        pattern = re.compile(phrase, flags=re.IGNORECASE)
        query = pattern.sub('', query)
    # remove any extra whitespace
    query = ' '.join(query.split())
    # return the cleaned query to be used in api calls
    return query

if __name__ == "__main__":
    print(retrieve_princeton_courses("baby"))
