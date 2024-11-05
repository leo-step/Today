from utils import get_embedding, openai_json_response, delete_dict_key_recursively, system_prompt, build_search_query
from clients import db_client
from prompts import get_course_search_prompt, user_query, extract_email_search_terms, email_search_query, extract_course_search_terms
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

# course scoring weights
TITLE_MATCH_SCORE = 10
DESCRIPTION_MATCH_SCORE = 5
EVALUATION_MATCH_SCORE = 8
COMMENT_MATCH_SCORE = 7
ASSIGNMENT_MATCH_SCORE = 6
COURSE_RATING_BELOW_35 = 1
COURSE_RATING_ABOVE_4 = 3
COURSE_QUALITY_DIFFICULTY = 10


def setup_mongodb_indices():
    # Email indices
    collection = db_client["crawl"]
    collection.create_index([
        ("source", 1),
        ("time", -1)
    ], name="source_time_idx")
    collection.create_index([
        ("subject", "text"),
        ("text", "text")
    ], name="email_text_idx")
    
    # course indices
    courses = db_client["courses"]
    
    # Drop existing text index if it exists
    try:
        courses.drop_index("course_text_idx")
    except:
        pass  # Index might not exist
        
    # Regular index for course code lookups
    courses.create_index([
        ("department", 1),
        ("catalogNumber", 1)
    ], name="course_code_idx")
    
    # Combined text index with weights and synonyms for thematic search
    courses.create_index([
        ("title", "text"),
        ("description", "text"),
        ("assignments", "text"),
        ("evaluations.comments.comment", "text")
    ], weights={
        "title": 10,
        "description": 8,
        "assignments": 3,
         "evaluations.comments.comment": 5
    }, default_language="english", name="course_text_idx")
    
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

def score_course_document(doc, search_info):
    """Score a course document based on search terms and query type"""
    score = 0
    terms = search_info.get("terms", [])
    query_type = search_info.get("query_type", "info")
    focus = search_info.get("focus", [])
    
    # base scoring for different fields
    for term in terms:
        # title matches (highest weight)
        if re.search(term, str(doc.get("title", "")), re.IGNORECASE):
            score += TITLE_MATCH_SCORE
            
        # description matches    
        if re.search(term, str(doc.get("description", "")), re.IGNORECASE):
            score += DESCRIPTION_MATCH_SCORE
            
        # assignment matches
        if re.search(term, str(doc.get("assignments", "")), re.IGNORECASE):
            score += ASSIGNMENT_MATCH_SCORE

    # assign min positive score if any term matches title or description
    if score == 0:
        if any(term.lower() in str(doc.get("title", "")).lower() for term in terms):
            score += 1
        elif any(term.lower() in str(doc.get("description", "")).lower() for term in terms):
            score += 1

    # query type specific scoring
    if query_type == "opinion":
        # for opinion queries, heavily weight evaluations and comments
        comments = doc.get("evaluations", {}).get("comments", [])
        comment_score = 0
        relevant_comments = 0
        
        for comment in comments:
            comment_text = comment.get("comment", "").lower()
            if any(term.lower() in comment_text for term in terms):
                comment_score += COMMENT_MATCH_SCORE
                relevant_comments += 1
        
        # boost score based on number of relevant comments
        if relevant_comments > 0:
            score += comment_score * (1 + (relevant_comments / 10))
            
        # consider course ratings
        course_quality = float(doc.get("scores", {}).get("Quality of Course", 0) or 0)
        if course_quality > 4.0:
            score += COURSE_RATING_ABOVE_4
        elif course_quality > 3.5:
            score += COURSE_RATING_BELOW_35

    elif query_type == "comparison" or query_type == "difficulty":
        # for difficulty/comparison queries, focus on workload and evaluations
        assignments = str(doc.get("assignments", "")).lower()
        
        # check for workload indicators in assignments
        if any(term in assignments for term in ["problem set", "pset", "homework", "weekly"]):
            score += 7
        if any(term in assignments for term in ["paper", "essay", "project"]):
            score += ASSIGNMENT_MATCH_SCORE # keep the same as assignment match score
            
        # consier course ratings
        if "difficulty" in focus:
            course_quality = float(doc.get("scores", {}).get("Quality of Course", 0) or 0)
            if course_quality > 4.0:
                score += COURSE_QUALITY_DIFFICULTY
            
        # check comments for difficulty/workload mentions
        comments = doc.get("evaluations", {}).get("comments", [])
        for comment in comments:
            comment_text = comment.get("comment", "").lower()
            if any(term in comment_text for term in ["difficult", "hard", "challenging", "easy", "workload"]):
                score += COMMENT_MATCH_SCORE

    elif query_type == "tips":
        # for tips queries focus on success strats in comments
        comments = doc.get("evaluations", {}).get("comments", [])
        for comment in comments:
            comment_text = comment.get("comment", "").lower()
            if any(term in comment_text for term in ["tip", "advice", "recommend", "suggest", "help", "success"]):
                score += COMMENT_MATCH_SCORE * 1.5  # higher weight for tips
                
    # handle assignment preferences
    assignments = str(doc.get("assignments", "")).lower()
    if "no paper" in str(terms).lower() and any(term in assignments for term in ["paper", "essay", "writing"]):
        score = 0  # exclude if papers not wanted
    
    if any(term in str(terms).lower() for term in ["pset", "problem set"]):
        if any(term in assignments for term in ["problem set", "pset", "homework"]):
            score += 8 # unironically dont touch this if you can help it 
            
    # distribution requirements
    distribution = doc.get("distribution", "")
    terms_str = " ".join(terms).lower()
    if any(dist in terms_str for dist in ["ec", "em", "la", "cd", "ha", "sa", "qcr", "sel", "sen"]):
        if distribution and distribution.lower() in terms_str:
            score += 15
            
    return score

def process_course_doc(doc, score=1):
    """Process a course document into standard format with all details"""
    processed = {
        "_id": doc["_id"],
        "department": doc.get("department", ""),
        "catalogNumber": doc.get("catalogNumber", ""),
        "title": doc.get("title", ""),
        "description": doc.get("description", ""),
        "assignments": doc.get("assignments", []),
        "distribution": doc.get("distribution", ""),
        "scores": doc.get("scores", {}),
        "score": score,
        "courseID": doc.get("courseID", ""),
        "evaluations": doc.get("evaluations", {})
    }
    
    processed["url"] = f"https://www.princetoncourses.com/course/{doc.get('courseID', '')}"
    
    return processed

def retrieve_princeton_courses(query_text):
    """Robust course retrieval with multiple search strategies."""
    collection = db_client["courses"]
    
    try:
        # Convert query to lowercase for case-insensitive matching
        query_lower = query_text.lower()
        
        # first: direct course code lookup
        course_match = re.search(r'([A-Za-z]{2,3})\s*(\d{3}[A-Za-z]*)', query_text)
        if course_match:
            dept, num = course_match.groups()
            exact_course = collection.find_one({
                "department": dept.upper(),
                "catalogNumber": num
            })
            if exact_course:
                # get semester ID and courseID to construct full course ID (before i wasnt getting the semester ID)
                semester_id = str(exact_course.get('semester', {}).get('_id', ''))
                course_id = exact_course.get('courseID', '')
                full_course_id = f"{semester_id}{course_id}"
                return {
                    "main_course": exact_course,
                    "other_courses": [],
                    "url": f"https://www.princetoncourses.com/course/{full_course_id}",
                    "is_current": True
                }

        # expand search terms w/ related keywords
        expanded_terms = [query_lower]
        
        # add common variations and related terms
        # this should be done using openAI api but as a quick bandage fix this works for now tbh
        term_expansions = {
            'entrepreneur': ['entrepreneurship', 'startup', 'business', 'innovation', 'venture', 'leadership'],
            'business': ['entrepreneurship', 'management', 'leadership', 'organization', 'enterprise'],
            'computer': ['programming', 'software', 'computing', 'computational', 'digital'],
            'math': ['mathematics', 'mathematical', 'computational', 'quantitative'],
            'history': ['historical', 'civilization', 'culture', 'society'],
            'science': ['scientific', 'research', 'laboratory', 'experimental'],
            'engineering': ['design', 'technology', 'technical', 'applied'],
            'art': ['visual', 'creative', 'design', 'studio'],
            'writing': ['composition', 'written', 'communication', 'literature'],
            'research': ['methodology', 'analysis', 'investigation', 'study']
        }

        # add expanded terms
        for base_term, expansions in term_expansions.items():
            if base_term in query_lower:
                expanded_terms.extend(expansions)

        # remove duplicates while preserving order
        expanded_terms = list(dict.fromkeys(expanded_terms))

        text_query = ' '.join(expanded_terms)
        
        # first: try text search w/ expanded terms
        results = list(collection.find(
            {"$text": {"$search": text_query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(50))

        if not results:
            # if no results from text search, try regex search
            regex_conditions = []
            for term in expanded_terms:
                regex_conditions.extend([
                    {"title": {"$regex": f".*{re.escape(term)}.*", "$options": "i"}},
                    {"description": {"$regex": f".*{re.escape(term)}.*", "$options": "i"}},
                    {"assignments": {"$regex": f".*{re.escape(term)}.*", "$options": "i"}},
                    {"evaluations.comments.comment": {"$regex": f".*{re.escape(term)}.*", "$options": "i"}}
                ])
            
            results = list(collection.find({"$or": regex_conditions}).limit(50))

        if not results:
            # try one more time with partial word matching
            regex_conditions = []
            for term in expanded_terms:
                if len(term) > 3:  # only use terms longer than 3 characters
                    regex_conditions.extend([
                        {"title": {"$regex": re.escape(term), "$options": "i"}},
                        {"description": {"$regex": re.escape(term), "$options": "i"}},
                        {"assignments": {"$regex": re.escape(term), "$options": "i"}},
                        {"evaluations.comments.comment": {"$regex": re.escape(term), "$options": "i"}}
                    ])
            
            results = list(collection.find({"$or": regex_conditions}).limit(50))

        if not results:
            return {
                "main_course": {},
                "other_courses": [],
                "url": None,
                "is_current": True
            }

        # score and rank results
        scored_results = []
        for doc in results:
            score = 0
            
            # base score from text match
            if hasattr(doc, 'score'):
                score += doc.score * 2
            
            # title match bonus
            title = doc.get('title', '').lower()
            if any(term in title for term in expanded_terms):
                score += TITLE_MATCH_SCORE
            
            # desc match bonus
            desc = doc.get('description', '').lower()
            if any(term in desc for term in expanded_terms):
                score += DESCRIPTION_MATCH_SCORE
            
            # course rating bonus
            course_quality = float(doc.get('scores', {}).get('Quality of Course', 0) or 0)
            if course_quality > 4.0:
                score += COURSE_RATING_ABOVE_4
            elif course_quality > 3.5:
                score += COURSE_RATING_BELOW_35
            
            # comment relevance bonus
            comments = doc.get('evaluations', {}).get('comments', [])
            relevant_comments = sum(1 for comment in comments 
                                 if any(term in comment.get('comment', '').lower() 
                                       for term in expanded_terms))
            if relevant_comments > 0:
                score += min(relevant_comments, 5)  # cap the bonus at 5 points (not sure why but AI recommends it)
            
            # minimum score (to prevent 0 score results)
            if score == 0:
                score = 0.1
            
            scored_results.append({
                "doc": doc,
                "score": score
            })

        # sort by score
        scored_results.sort(key=lambda x: x["score"], reverse=True)

        # get top results
        main_course = scored_results[0]["doc"]
        other_courses = [r["doc"] for r in scored_results[1:5]]

        # clean up main course object
        main_course = {k: v for k, v in main_course.items()
                      if k not in ['_id', 'embedding', 'score']}

        # format other courses
        other_courses = [{
            "department": c.get("department", ""),
            "catalogNumber": c.get("catalogNumber", ""),
            "title": c.get("title", "")
        } for c in other_courses]

        # construct course URL
        semester_id = str(main_course.get('semester', {}).get('_id', ''))
        course_id = main_course.get('courseID', '')
        full_course_id = f"{semester_id}{course_id}"

        return {
            "main_course": main_course,
            "other_courses": other_courses,
            "url": f"https://www.princetoncourses.com/course/{full_course_id}",
            "is_current": True
        }

    except Exception as e:
        print("[ERROR] Course retrieval failed:", e)
        return {
            "main_course": {},
            "other_courses": [],
            "url": None,
            "is_current": True
        }

# this does not fucking work, my brain is not working and i can't
# youd think i could just copypaste from the old function to use this a fallback
# but i *cannot* get it to work idk why but i going to bed before i cry
def get_course_from_princetoncourses(dept, num):
    """Attempt to get course information directly from princetoncourses.com"""
    try:
        # first try via course ID
        search_url = f"https://princetoncourses.com/search/{dept}{num}"
        search_response = requests.get(search_url)
        if not search_response.ok:
            return None
        
        search_data = search_response.json()
        if not search_data or not search_data.get("courses"):
            return None
            
        course_id = search_data["courses"][0].get("courseID")
        if not course_id:
            return None
            
        # get full course details
        course_url = f"https://princetoncourses.com/course/{course_id}"
        course_response = requests.get(course_url)
        if not course_response.ok:
            return None
            
        course_data = course_response.json()
        if not course_data:
            return None
            
        # process the course data into standard format
        processed_course = {
            "_id": course_id,
            "department": dept,
            "catalogNumber": num,
            "title": course_data.get("title", ""),
            "description": course_data.get("description", ""),
            "assignments": course_data.get("assignments", []),
            "distribution": course_data.get("distribution", ""),
            "scores": course_data.get("scores", {}),
            "courseID": course_id,
            "evaluations": course_data.get("evaluations", {}),
            "score": 1  # default score since direct lookup (i think this is how u do it)
        }
        
        return processed_course
    except Exception as e:
        print(f"[ERROR] Failed to fetch course from princetoncourses: {e}")
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