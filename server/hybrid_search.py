from utils import get_embedding
import time

def hybrid_search(collection, query, source=None, expiry=False, sort=None, max_results=5):
    query_vector = get_embedding(query)

    current_time = int(time.time())

    # build filter condition
    filter_condition = {}
    if source:
        filter_condition["source"] = source
    if expiry:
        filter_condition["expiry"] = { "$gt": current_time }

    ### Vector Search Pipeline
    vector_pipeline = [
        {
            "$vectorSearch": {
                "queryVector": query_vector,
                "path": "embedding",
                "numCandidates": 50,
                "limit": 50,
                "index": "vector_index"
            }
        },
        {
            "$addFields": {
                "score": { "$meta": "vectorSearchScore" }
            }
        },
        {
            "$project": {
                "_id": 1,
                "text": 1,
                "links": 1,
                "time": 1,
                "source": 1,
                "score": 1
            }
        }
    ]

    if filter_condition:
        vector_pipeline.insert(1, { "$match": filter_condition })

    if sort:
        vector_pipeline.append({ "$sort": dict(sort) })

    vector_results = collection.aggregate(vector_pipeline)
    vector_docs = list(vector_results)

    ### Keyword Search Pipeline
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
        {
            "$addFields": {
                "score": { "$meta": "searchScore" }
            }
        },
        {
            "$project": {
                "_id": 1,
                "text": 1,
                "links": 1,
                "time": 1,
                "source": 1,
                "score": 1
            }
        }
    ]

    if filter_condition:
        keyword_pipeline.insert(1, { "$match": filter_condition })

    # apply sorting if specified
    if sort:
        keyword_pipeline.append({ "$sort": dict(sort) })
    else:
        keyword_pipeline.append({ "$sort": { "score": -1 } })

    keyword_results = collection.aggregate(keyword_pipeline)
    keyword_docs = list(keyword_results)

    # combine and deduplicate results
    doc_lists = [vector_docs, keyword_docs]
    for i in range(len(doc_lists)):
        doc_lists[i] = [
            {
                "_id": str(doc["_id"]),
                "text": doc["text"],
                "links": doc.get("links", []),
                "time": doc.get("time"),
                "source": doc.get("source"),
                "score": doc["score"]
            }
            for doc in doc_lists[i]
        ]

    # fuse results using weighted reciprocal rank
    fused_documents = weighted_reciprocal_rank(doc_lists)

    # return top results up to max_results
    return fused_documents[:max_results]

def weighted_reciprocal_rank(doc_lists):
    """
    Perform weighted Reciprocal Rank Fusion on multiple rank lists.
    """
    c = 60  # constant from the RRF paper
    weights = [1] * len(doc_lists)  # equal weights for all lists

    # create a union of all unique docs
    all_documents = set()
    for doc_list in doc_lists:
        for doc in doc_list:
            all_documents.add(doc["text"])

    # initialize RRF score dictionary
    rrf_score_dic = {doc: 0.0 for doc in all_documents}

    # calc RRF scores
    for doc_list, weight in zip(doc_lists, weights):
        for rank, doc in enumerate(doc_list, start=1):
            rrf_score = weight * (1 / (c + rank))
            rrf_score_dic[doc["text"]] += rrf_score

    # sort docs by RRF scores
    sorted_documents = sorted(
        rrf_score_dic.keys(), key=lambda x: rrf_score_dic[x], reverse=True
    )

    # map sorted content back to doc objects
    page_content_to_doc_map = {
        doc["text"]: doc for doc_list in doc_lists for doc in doc_list
    }
    sorted_docs = [
        page_content_to_doc_map[content] for content in sorted_documents
    ]

    return sorted_docs
