from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pymongo.collection import Collection
from langchain_openai import OpenAIEmbeddings
from pydantic import Field

class MongoHybridRetriever(BaseRetriever):
    collection: Collection = Field(..., description="The name or identifier of the MongoDB collection")
    embeddings: OpenAIEmbeddings = Field(..., description="Embeddings model used for vector search")
    vector_penalty = 1
    full_text_penalty = 1
    vector_num_candidates = 100
    vector_limit = 20
    fts_limit = 20
    limit = 10

    def _get_relevant_documents(self, query: str):
        docs = self.perform_hybrid_search(query)
        return [Document(page_content=doc['_id']) for doc in docs]

    def perform_hybrid_search(self, query):
        query_vector = self.embeddings.embed_query(query)
        result = self.collection.aggregate([
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": self.vector_num_candidates,
                    "limit": self.vector_limit
                }
            },
            {
                "$group": {
                    "_id": None,
                    "docs": {"$push": "$$ROOT"}
                }
            },
            {
                "$unwind": {
                    "path": "$docs",
                    "includeArrayIndex": "rank"
                }
            },
            {
                "$addFields": {
                    "vs_score": {
                        "$divide": [1.0, {"$add": ["$rank", self.vector_penalty, 1]}]
                    }
                }
            },
            {
                "$project": {
                    "vs_score": 1,
                    "_id": "$docs._id",
                    "text": "$docs.text"
                }
            },
            {
                "$unionWith": {
                    "coll": "crawl",
                    "pipeline": [
                        {
                            "$search": {
                                "index": "full-text-search",
                                "phrase": {
                                    "query": query,
                                    "path": "text"
                                }
                            }
                        },
                        {
                            "$limit": self.fts_limit
                        },
                        {
                            "$group": {
                                "_id": None,
                                "docs": {"$push": "$$ROOT"}
                            }
                        },
                        {
                            "$unwind": {
                                "path": "$docs",
                                "includeArrayIndex": "rank"
                            }
                        },
                        {
                            "$addFields": {
                                "fts_score": {
                                    "$divide": [
                                        1.0,
                                        {"$add": ["$rank", self.full_text_penalty, 1]}
                                    ]
                                }
                            }
                        },
                        {
                            "$project": {
                                "fts_score": 1,
                                "_id": "$docs._id",
                                "text": "$docs.text"
                            }
                        }
                    ]
                }
            },
            {
                "$group": {
                    "_id": "$text",
                    "vs_score": {"$max": "$vs_score"},
                    "fts_score": {"$max": "$fts_score"}
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "text": 1,
                    "vs_score": {"$ifNull": ["$vs_score", 0]},
                    "fts_score": {"$ifNull": ["$fts_score", 0]}
                }
            },
            {
                "$project": {
                    "score": {"$add": ["$fts_score", "$vs_score"]},
                    "_id": 1,
                    "text": 1,
                    "vs_score": 1,
                    "fts_score": 1
                }
            },
            {
                "$sort": {"score": -1}
            },
            {
                "$limit": self.limit
            }
        ])
        return [doc for doc in result]
