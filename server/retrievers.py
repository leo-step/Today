from utils import get_embedding
from clients import db_client

def retrieve_crawl(query_text):
    collection = db_client["today"]["crawl"]
    return hybrid_search(collection, query_text)

def retrieve_emails(query_text):
    collection = db_client["today"]["emails"]
    return hybrid_search(collection, query_text)

def hybrid_search(collection, query_text):
    query_vector = get_embedding(query_text)
    vector_results = collection.aggregate([
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 20,
                "limit": 5
            }
        },
        {
            "$project": {
                "_id": 1,
                "text": 1,
                "links": 1,
                "time": 1,
                "vs_score": {
                    "$divide": [1.0, {"$add": [{"$indexOfArray": [None, "$_id"]}, 1, 1]}]
                }
            }
        }
    ])

    full_text_results = collection.aggregate([
        {
            "$search": {
                "index": "full-text-search",
                "phrase": {
                    "query": query_text,
                    "path": "text"
                }
            }
        },
        {
            "$limit": 5
        },
        {
            "$project": {
                "_id": 1,
                "text": 1,
                "links": 1, 
                "time": 1,
                "fts_score": {
                    "$divide": [1.0, {"$add": [{"$indexOfArray": [None, "$_id"]}, 1, 1]}]
                }
            }
        }
    ])
    
    vector_results = list(vector_results)
    full_text_results = list(full_text_results)

    combined_results = vector_results + full_text_results
    
    for doc in combined_results:
        vs_score = doc.get('vs_score', 0) if doc.get('vs_score') is not None else 0
        fts_score = doc.get('fts_score', 0) if doc.get('fts_score') is not None else 0
        doc['score'] = vs_score + fts_score

    sorted_results = sorted(combined_results, key=lambda x: x['score'], reverse=True)[:5]
    return sorted_results
