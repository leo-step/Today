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
    return hybrid_search(collection, query_text, source="map")

def retrieve_crawl(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text, source="web")

def retrieve_emails(query_text):
    collection = db_client["crawl"]
    current_time = int(time.time())
    
    # extract important search terms
    # ignore time related words bc that's not relevant for email search
    # emails get filterd by time after all possible results are retrieved
    search_info = openai_json_response([{
        "role": "system",
        "content": """Extract ONLY the specific items, topics, or subjects being asked about. Ignore all helper words, time words, and generic terms like 'events', 'things', 'activities', 'announcements', etc.
        Return a JSON with:
        - 'terms': array of ONLY the specific items/topics being searched for
        
        Examples:
        "is there any free pizza available right now?" -> {"terms": ["free pizza", "pizza"]}
        "are there any israel/palestine related events right now? or soon?" -> {"terms": ["israel", "palestine"]}
        "what events are there about israel or palestine?" -> {"terms": ["israel", "palestine"]}
        "was there free fruit yesterday?" -> {"terms": ["fruit", "free fruit"]}
        "when is the next narcan training session today?" -> {"terms": ["narcan", "narcan training"]}
        "any fruit related events happening now?" -> {"terms": ["fruit"]}
        "were there any tacos and olives on campus?" -> {"terms": ["tacos", "olives"]}
        "is there anything about israel going on right now?" -> {"terms": ["israel"]}
        "was there any free food yesterday in the kanji lobby?" -> {"terms": ["free food", "kanji lobby"]}
        "are there any events about climate change tomorrow?" -> {"terms": ["climate change"]}
        "what's happening with SJP this week?" -> {"terms": ["sjp"]}
        "any fruit bowls available today?" -> {"terms": ["fruit bowl", "fruit"]}
        "when is the next a cappella performance?" -> {"terms": ["a cappella"]}
        "are there any dance shows this weekend?" -> {"terms": ["dance"]}
        "is there volleyball practice tonight?" -> {"terms": ["volleyball"]}
        "any meditation sessions happening soon?" -> {"terms": ["meditation"]}
        "where can I find free coffee right now?" -> {"terms": ["free coffee", "coffee"]}
        "is the chess club meeting today?" -> {"terms": ["chess club", "chess"]}
        "any robotics workshops this week?" -> {"terms": ["robotics"]}
        "when's the next movie screening?" -> {"terms": ["movie screening", "movie"]}
        "are there any study groups for organic chemistry?" -> {"terms": ["organic chemistry"]}
        "is anyone giving away free textbooks?" -> {"terms": ["free textbooks", "textbooks"]}
        "what time is the math help session?" -> {"terms": ["math help"]}
        "are there any filipino events on campus?" -> {"terms": ["filipino"]}
        "are there any events about palestine happening today?" -> {"terms": ["palestine"]}
        "what fruit events were there yesterday?" -> {"terms": ["fruit"]}"""
    }, {
        "role": "user",
        "content": query_text
    }])
    
    search_terms = search_info["terms"]
    print(f"[DEBUG] Search terms: {search_terms}")
    
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
        "now", "current", "today", "happening", "right now"
    ])
    include_past = any(word in query_text.lower() for word in [
        "yesterday", "past", "previous", "before", "earlier", "last"
    ])
    
    # the following filters are arbitrarily chose, but these work pretty well
    # in my testing; feel free to change as necessary

    if is_current:
        # for current queries only show events from last 12hours
        processed_results = [
            doc for doc in processed_results 
            if (current_time - doc["metadata"]["time"]) < 12 * 3600
        ]
    elif include_past:
        # for past queries show everything from last 14 days
        processed_results = [
            doc for doc in processed_results 
            if (current_time - doc["metadata"]["time"]) < 14 * 24 * 3600
        ]
    else:
        # default to last week
        processed_results = [
            doc for doc in processed_results 
            if (current_time - doc["metadata"]["time"]) < 24 * 3600 * 7
        ]
    
    return processed_results[:10]

def retrieve_any_emails(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text, source="email")

def retrieve_eating_clubs(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text, source="eatingclub", expiry=True)

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

def hybrid_search(collection, query, source=None, time_filter=None, max_results=5, sort=None, exact_match=False):
    current_time = int(time.time())
    embedding = get_embedding(query)

    # text search pipeline w/ exact match option
    text_pipeline = [
        {
            "$search": {
                "index": "default",
                "compound": {
                    "should": [
                        {
                            "text": {
                                "query": query,
                                "path": ["text", "metadata.subject"],
                                "fuzzy": {} if not exact_match else None
                            }
                        },
                        {
                            "phrase": {
                                "query": query,
                                "path": ["text", "metadata.subject"],
                                "score": { "boost": { "value": 2 } }
                            }
                        }
                    ]
                }
            }
        },
        {
            "$addFields": {
                "score": {"$meta": "searchScore"},
                "age": {"$subtract": [current_time, "$metadata.time"]}
            }
        }
    ]

    # vector search pipeline
    vector_pipeline = [
        {
            "$search": {
                "index": "default",
                "knnBeta": {
                    "vector": embedding,
                    "path": "embedding",
                    "k": max_results * 2
                }
            }
        },
        {
            "$addFields": {
                "score": {"$meta": "searchScore"},
                "age": {"$subtract": [current_time, "$metadata.time"]}
            }
        }
    ]

    # apply filters to both pipelines
    match_filter = {}
    if source:
        match_filter["metadata.source"] = source
    if time_filter:
        match_filter.update(time_filter)
    
    if match_filter:
        vector_pipeline.insert(1, {"$match": match_filter})
        text_pipeline.insert(1, {"$match": match_filter})

    # project fields for both pipelines
    projection = {
        "$project": {
            "_id": 1,
            "text": 1,
            "links": 1,
            "metadata": 1,
            "score": 1,
            "age": 1
        }
    }
    vector_pipeline.append(projection)
    text_pipeline.append(projection)

    # add time decay to scores
    time_decay = {
        "$addFields": {
            "score": {
                "$multiply": [
                    "$score",
                    {"$exp": {"$multiply": [-0.0000001, "$age"]}}
                ]
            }
        }
    }
    vector_pipeline.append(time_decay)
    text_pipeline.append(time_decay)

    # execute both pipelines
    vector_results = list(collection.aggregate(vector_pipeline))
    text_results = list(collection.aggregate(text_pipeline))

    # combine results and remove duplicates
    seen_ids = set()
    all_results = []
    
    # process and deduplicate results; prioritizing text matches
    for doc in text_results + vector_results:  # text results come first
        doc_id = str(doc["_id"])
        if doc_id not in seen_ids:
            seen_ids.add(doc_id)
            processed_doc = {
                "_id": doc_id,
                "text": doc["text"],
                "links": doc.get("links", []),
                "metadata": doc.get("metadata", {}),
                "score": doc.get("score", 0),
                "age": doc.get("age", 0)
            }

            # Add time context
            age_days = doc["age"] / (24 * 3600)
            if age_days > 30:
                processed_doc["time_context"] = f"[WARNING] This information is from {int(age_days)} days ago and may be outdated."
            elif age_days > 7:
                processed_doc["time_context"] = f"[NOTE] This information is from {int(age_days)} days ago."
            elif age_days > 1:
                processed_doc["time_context"] = f"[RECENT] This information is from {int(age_days)} days ago."
            else:
                processed_doc["time_context"] = "[CURRENT] This information is from today."

            all_results.append(processed_doc)

    # sort by score
    all_results.sort(key=lambda x: x["score"], reverse=True)
    
    return all_results[:max_results]

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

