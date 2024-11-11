from utils import get_embedding, openai_json_response, delete_dict_key_recursively, system_prompt, build_search_query
from clients import db_client
from prompts import user_query, extract_email_search_terms, email_search_query, extract_course_search_terms
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
DESCRIPTION_MATCH_SCORE = 6
COMMENT_MATCH_SCORE = 7
ASSIGNMENT_MATCH_SCORE = 6
COURSE_RATING_BELOW_35 = 4
COURSE_RATING_ABOVE_4 = 5
GRADING_COMPONENT_BOOST = 10

# dist req mappings
DISTRIBUTION_MAPPINGS = {
    "humanities": ["LA", "HA", "SA", "EM", "CD", "EC"], 
    "science": ["STL", "SEL", "SEN"],
    "quantitative": ["QCR", "QR"],
    "writing": ["EC", "SA", "WRI"],
    "ethics": ["EM"],
    "culture": ["CD"],
    "history": ["HA"],
    "arts": ["LA"],
    "social": ["SA"],
}

# assignment type indicators
PSET_INDICATORS = [
    "problem set", "pset", "problem sets", "psets", 
    "p-set", "problem-set", "computational assignment", "mathematical assignment"
]

PAPER_INDICATORS = [
    "paper", "essay", "writing assignment", "written assignment",
    "research paper", "term paper", "papers", "essays"
]

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
        
    courses.create_index([
        ("department", 1),
        ("catalogNumber", 1)
    ], name="course_code_idx")
    
    courses.create_index([
        ("title", "text"),
        ("description", "text"),
        ("assignments", "text"),
        ("semesters.evaluations.comments.comment", "text")
    ], weights={
        "title": 10,
        "description": 8,
        "assignments": 3,
        "semesters.evaluations.comments.comment": 5
    }, default_language="english", name="course_text_idx")
    
    courses.create_index([("semesters.semester._id", -1)])  # sorting by most recent semester
    courses.create_index([("semesters.scores.Quality of Course", -1)])  # course quality lookups
    
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
    """Score a course document based on search terms."""
    score = 0
    terms = search_info.get("terms", [])
    course_codes = search_info.get("course_codes", [])
    query_type = search_info.get("query_type", "")

    # For comparison queries, ensure both courses get a base score
    if query_type == "comparison" and course_codes:
        dept = doc.get("department", "")
        catalog = doc.get("catalogNumber", "")
        course_code = f"{dept}{catalog}"
        if course_code in course_codes:
            score = 1  # Base score for compared courses

    # Base scoring for different fields
    for term in terms:
        # Department matches (highest weight)
        if re.search(f"^{re.escape(term)}$", str(doc.get("department", "")), re.IGNORECASE):
            score += TITLE_MATCH_SCORE * 2

        # Title matches (high weight)
        if re.search(term, str(doc.get("title", "")), re.IGNORECASE):
            score += TITLE_MATCH_SCORE

        # Description matches
        if re.search(term, str(doc.get("description", "")), re.IGNORECASE):
            score += DESCRIPTION_MATCH_SCORE

        # Assignment matches
        if re.search(term, " ".join(doc.get("assignments", [])), re.IGNORECASE):
            score += ASSIGNMENT_MATCH_SCORE

        # Comment matches
        if doc.get("semesters"):
            comment_count = 0
            max_comments = 5
            
            for sem in doc["semesters"][:2]:  # Only check last 2 semesters
                if sem.get("evaluations", {}).get("comments"):
                    for comment in sem["evaluations"]["comments"]:
                        if comment_count >= max_comments:
                            break
                        if re.search(term, str(comment.get("comment", "")), re.IGNORECASE):
                            score += COMMENT_MATCH_SCORE
                            comment_count += 1

    # Course level boost based on catalog number
    catalog_num = doc.get("catalogNumber", "")
    if catalog_num:
        level = catalog_num[0] if catalog_num.isdigit() else None
        if level:
            # Boost score for appropriate level courses
            if any("sophomore" in term.lower() for term in terms) and level == "2":
                score *= 1.5
            elif any("junior" in term.lower() for term in terms) and level == "3":
                score *= 1.5
            elif any("senior" in term.lower() for term in terms) and level == "4":
                score *= 1.5

    # Quality boost
    course_quality = 0
    if doc.get("semesters"):
        for sem in doc["semesters"]:
            if sem.get("scores", {}).get("Quality of Course"):
                course_quality = float(sem["scores"]["Quality of Course"])
                break

    if course_quality > 4.0:
        score += COURSE_RATING_ABOVE_4
    elif course_quality > 3.5:
        score += COURSE_RATING_BELOW_35

    # Scoring for assignments
    assignments = doc.get("assignments", [])
    if any(indicator in assignment.lower() for assignment in assignments for indicator in PSET_INDICATORS):
        score += GRADING_COMPONENT_BOOST

    # Scoring for grading components
    grading = doc.get("grading", [])
    if any(indicator in component.get("component", "").lower() for component in grading for indicator in PSET_INDICATORS):
        score += GRADING_COMPONENT_BOOST

    return score

def has_assignment_type(doc, indicators):
    """Check if a course has a particular type of assignment."""
    assignments = " ".join(doc.get("assignments", [])).lower()
    grading_components = " ".join(component.get("component", "").lower() for component in doc.get("grading", []))

    # Check assignments and grading components
    return any(indicator in assignments for indicator in indicators) or any(indicator in grading_components for indicator in indicators)

def matches_distribution(doc, dist_type):
    """Check if a course matches a distribution requirement category."""
    course_dist = str(doc.get("distribution", "")).split(" OR ")

    # Get valid distribution codes for the type
    valid_codes = DISTRIBUTION_MAPPINGS.get(dist_type.lower(), [])

    return any(dist in valid_codes for dist in course_dist)

def retrieve_princeton_courses(query_text):
    """Retrieve courses from the database based on the query."""
    collection = db_client["courses"]

    try:
        # Get search terms
        search_info = openai_json_response([
            extract_course_search_terms(),
            user_query(query_text)
        ])

        search_terms = search_info.get("terms", [])
        course_codes = search_info.get("course_codes", [])
        query_type = search_info.get("query_type", "")
        print(f"[DEBUG] Course search terms: {search_terms}")
        print(f"[DEBUG] Course codes: {course_codes}")
        print(f"[DEBUG] Query type: {query_type}")

        # If no terms, return empty results
        if not search_terms:
            return {
                "main_course": {},
                "main_courses": [],
                "other_courses": [],
                "url": None,
                "is_current": True
            }

        # For comparison queries, directly fetch the specific courses
        if query_type == "comparison" and course_codes:
            compare_conditions = []
            for code in course_codes:
                if len(code) >= 3:
                    # Split the course code into department and number, handling spaces
                    parts = code.split()
                    if len(parts) == 2:
                        dept, num = parts
                    else:
                        dept = code[:3]
                        num = code[3:]
                    compare_conditions.append({
                        "$and": [
                            {"department": dept},
                            {"catalogNumber": num}
                        ]
                    })
            base_query = {"$or": compare_conditions}
            
            # For comparison queries, include all semester data
            matches = list(collection.find(base_query))
        else:
            # Build search conditions for non-comparison queries
            search_conditions = []
            for term in search_terms:
                search_conditions.extend([
                    {"department": {"$regex": f".*{re.escape(term)}.*", "$options": "i"}},
                    {"title": {"$regex": f".*{re.escape(term)}.*", "$options": "i"}},
                    {"description": {"$regex": f".*{re.escape(term)}.*", "$options": "i"}},
                    {"assignments": {"$regex": f".*{re.escape(term)}.*", "$options": "i"}},
                    {"semesters.evaluations.comments.comment": {"$regex": f".*{re.escape(term)}.*", "$options": "i"}},
                    {"prerequisites": {"$regex": f".*{re.escape(term)}.*", "$options": "i"}},
                    {"catalogNumber": {"$regex": f".*{re.escape(term)}.*", "$options": "i"}}
                ])
            base_query = {"$or": search_conditions}

            # Add exclusion for already taken courses
            if course_codes and query_type != "comparison":
                exclude_conditions = []
                for code in course_codes:
                    if len(code) >= 3:
                        dept = code[:3]
                        num = code[3:]
                        exclude_conditions.append({
                            "$and": [
                                {"department": dept},
                                {"catalogNumber": num}
                            ]
                        })
                if exclude_conditions:
                    base_query = {
                        "$and": [
                            base_query,
                            {"$nor": exclude_conditions}
                        ]
                    }
            
            matches = list(collection.find(base_query))

        print(f"[DEBUG] Found {len(matches)} matching courses")

        # Apply extra filters on query
        filtered_matches = []
        query_lower = query_text.lower()

        # Check distribution requirements
        dist_type = None
        for dist in DISTRIBUTION_MAPPINGS.keys():
            if dist in query_lower:
                dist_type = dist
                break

        # Check assignment types
        needs_psets = any(term in query_lower for term in PSET_INDICATORS)
        needs_papers = any(term in query_lower for term in PAPER_INDICATORS)

        # Filter based on requirements
        for doc in matches:
            matches_requirements = True
            
            # Skip requirement filtering for comparison queries to ensure both courses are included
            if query_type != "comparison":
                if dist_type and not matches_distribution(doc, dist_type):
                    matches_requirements = False

                if needs_psets and not has_assignment_type(doc, PSET_INDICATORS):
                    matches_requirements = False
                if needs_papers and not has_assignment_type(doc, PAPER_INDICATORS):
                    matches_requirements = False

                # Level-based filtering using catalog number
                catalog_num = doc.get("catalogNumber", "")
                if catalog_num and catalog_num.isdigit():
                    level = catalog_num[0]
                    # Check for level requirements in search terms
                    if any("sophomore" in term.lower() for term in search_terms) and level not in ["2", "3"]:
                        matches_requirements = False
                    elif any("junior" in term.lower() for term in search_terms) and level not in ["3", "4"]:
                        matches_requirements = False
                    elif any("senior" in term.lower() for term in search_terms) and level not in ["4", "5"]:
                        matches_requirements = False

            if matches_requirements:
                filtered_matches.append(doc)

        # Score and sort
        scored_results = []
        for doc in filtered_matches:
            score = score_course_document(doc, search_info)
            if score > 0:
                # Apply level-based score boost
                catalog_num = doc.get("catalogNumber", "")
                if catalog_num and catalog_num.isdigit():
                    level = catalog_num[0]
                    if any("sophomore" in term.lower() for term in search_terms) and level == "2":
                        score *= 1.5
                    elif any("junior" in term.lower() for term in search_terms) and level == "3":
                        score *= 1.5
                    elif any("senior" in term.lower() for term in search_terms) and level == "4":
                        score *= 1.5

                # Boost scores based on query type
                if search_info.get("query_type") == "difficulty":
                    # Boost courses with clear workload information
                    if any("workload" in str(comment.get("comment", "")).lower() 
                          for sem in doc.get("semesters", [])
                          for comment in sem.get("evaluations", {}).get("comments", [])):
                        score *= 1.3
                elif search_info.get("query_type") == "prerequisites":
                    # Boost courses with clear prerequisite information
                    if doc.get("prerequisites"):
                        score *= 1.3

                doc["score"] = score
                scored_results.append(doc)

        scored_results.sort(key=lambda x: x.get("score", 0), reverse=True)

        if not scored_results:
            return {
                "main_course": {},
                "main_courses": [],
                "other_courses": [],
                "url": None,
                "is_current": True
            }

        # Process all courses
        processed_courses = []
        for course in scored_results:  # Process all scored courses
            # For comparison queries, ensure both courses are included with minimal processing
            if query_type == "comparison":
                dept = course.get("department", "")
                catalog = course.get("catalogNumber", "")
                # Try both formats to match course codes
                course_code_with_space = f"{dept} {catalog}"
                course_code_no_space = f"{dept}{catalog}"
                
                if course_code_with_space in course_codes or course_code_no_space in course_codes:
                    processed_course = course.copy()  # Keep all original data including semesters
                    
                    # Sort and limit semesters if they exist
                    if processed_course.get("semesters"):
                        processed_course["semesters"].sort(key=lambda x: x.get("semester", {}).get("_id", 0), reverse=True)
                        processed_course["semesters"] = processed_course["semesters"][:2]  # Get 2 most recent semesters
                        
                        # Process comments for each semester
                        for semester in processed_course["semesters"]:
                            if semester.get("evaluations", {}).get("comments"):
                                comments = semester["evaluations"]["comments"]
                                relevant_comments = []
                                
                                for comment in comments:
                                    comment_text = comment.get("comment", "").lower()
                                    if any(keyword in comment_text for keyword in ["difficult", "easy", "workload", "time", "hours", "assignments", "exams", "lectures"]):
                                        relevant_comments.append(comment)
                                    if len(relevant_comments) >= 5:  # Keep up to 5 relevant comments
                                        break
                                
                                semester["evaluations"]["comments"] = relevant_comments
                    
                    processed_courses.append(processed_course)
            else:
                # Normal processing for non-comparison queries
                max_semesters = 2  # Default to 2 semesters
                max_comments = 5   # Default to 5 comments per semester
                
                if query_type == "major":
                    max_semesters = 1
                    max_comments = 3
                elif query_type == "difficulty":
                    max_semesters = 2
                    max_comments = 4
                elif query_type == "opinion":
                    max_semesters = 3
                    max_comments = 5

                # Limit semesters and comments
                if course.get("semesters"):
                    course["semesters"].sort(key=lambda x: x.get("semester", {}).get("_id", 0), reverse=True)
                    course["semesters"] = course["semesters"][:max_semesters]
                    
                    for sem in course["semesters"]:
                        if sem.get("evaluations", {}).get("comments"):
                            comments = sem["evaluations"]["comments"]
                            relevant_comments = []
                            
                            for comment in comments:
                                comment_text = comment.get("comment", "").lower()
                                is_relevant = False
                                
                                if query_type == "difficulty":
                                    is_relevant = any(term in comment_text for term in ["difficult", "easy", "workload", "time", "hours"])
                                elif query_type == "prerequisites":
                                    is_relevant = any(term in comment_text for term in ["prerequisite", "background", "prepare", "need to know"])
                                else:
                                    is_relevant = True
                                
                                if is_relevant:
                                    relevant_comments.append(comment)
                                    if len(relevant_comments) >= max_comments:
                                        break
                            
                            sem["evaluations"]["comments"] = relevant_comments[:max_comments]
                
                processed_courses.append(course)

        # Get the top courses (all courses for comparison, up to 20 for others)
        main_courses = processed_courses[:20] if query_type != "comparison" else processed_courses

        # Get semester ID and course ID to construct full course ID for first course
        first_course = main_courses[0] if main_courses else None
        semester_id = str(first_course.get('semester', {}).get('_id', '')) if first_course else ''
        course_id = first_course.get('courseID', '') if first_course else ''
        full_course_id = f"{semester_id}{course_id}"

        # Format other courses info (remaining courses after top 20)
        other_courses = [] if query_type == "comparison" else [{
            "department": c.get("department", ""),
            "catalogNumber": c.get("catalogNumber", ""),
            "title": c.get("title", ""),
            "description": c.get("description", ""),
            "prerequisites": c.get("prerequisites", ""),
            "distribution": c.get("distribution", "")
        } for c in processed_courses[20:40]]

        return {
            "main_course": first_course if first_course else {},
            "main_courses": main_courses,
            "other_courses": other_courses,
            "url": f"https://www.princetoncourses.com/course/{full_course_id}" if full_course_id else None,
            "is_current": True
        }

    except Exception as e:
        print("[ERROR] Course retrieval failed:", e)
        return {
            "main_course": {},
            "main_courses": [],
            "other_courses": [],
            "url": None,
            "is_current": True
        }

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