from utils import get_embedding, openai_json_response, delete_dict_key_recursively
from clients import db_client
import time
import requests
from prompts import get_courses_search_query, user_query
import os

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
    return hybrid_search(collection, query_text, "email", expiry=True)

def retrieve_any_emails(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text, "email")

def retrieve_princeton_courses(query_text):
    response = openai_json_response([
        get_courses_search_query(),
        user_query(query_text)
    ])
    search_query = response["search_query"]
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
                course_id = search_results[0]["_id"]
                response = requests.get(f"https://www.princetoncourses.com/api/course/{course_id}", headers=headers)
                data = delete_dict_key_recursively(response.json(), "courses")
                data = delete_dict_key_recursively(data, "course")
                data = delete_dict_key_recursively(data, "_id")
                return data, i == 0
            except:
                print("[ERROR] response 1 failed")
                return {}, True
    except:
        print("[ERROR] response 2 failed")
        return {}, True

def retrieve_any(query_text):
    collection = db_client["crawl"]
    return hybrid_search(collection, query_text)


def hybrid_search(collection, query_text, source=None, expiry=False, max_results=5):
    query_vector = get_embedding(query_text)

    vector_pipeline = [
        {
            "$vectorSearch":
                {
                    "queryVector": query_vector,
                    "path": "embedding",
                    "numCandidates": 50,
                    "limit": 5,
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

    if expiry:
        vector_pipeline[0]["$vectorSearch"]["filter"] = {
            "$and": [
                {
                    "source": {
                        "$eq": source
                    }
                },
                {
                    "expiry": {
                        "$gt": int(time.time())
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
                    "query": query_text,
                    "path": "text"
                }
            }
        },
        { "$addFields" : { "score": { "$meta": "searchScore" } } },
        { "$limit": 5 }
    ]

    if source:
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

if __name__ == "__main__":
    print(retrieve_princeton_courses("baby"))
