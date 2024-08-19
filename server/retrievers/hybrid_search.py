from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pymongo.collection import Collection
from langchain_openai import OpenAIEmbeddings
from pydantic import Field
import time

class MongoHybridRetriever(BaseRetriever):
    collection: Collection = Field(..., description="The name or identifier of the MongoDB collection")
    embeddings: OpenAIEmbeddings = Field(..., description="Embeddings model used for vector search")
    vector_penalty = 1
    full_text_penalty = 1
    vector_num_candidates = 25
    vector_limit = 5
    fts_limit = 5
    limit = 5

    def get_time_ago(self, doc_time: int) -> str:
        current_time = int(time.time())
        time_difference = current_time - doc_time
        
        days_ago = time_difference // (24 * 3600)
        
        if days_ago == 0:
            return "Today"
        elif days_ago == 1:
            return "1 day ago"
        else:
            return f"{days_ago} days ago"
        
    def clean_up_links(self, links):
        # exclude various garbage links
        return links

    def _get_relevant_documents(self, query: str):
        docs = self.perform_hybrid_search(query)
        for doc in docs:
            if doc["url"]: # TODO: this should just be a schema change in data pipeline
                doc["links"] = [doc["url"]]
            links = "\n".join(self.clean_up_links(doc["links"]))
            time_ago = self.get_time_ago(doc["time"])
            metadata_text = f"\n\nLinks: {links}\nHow recent? {time_ago}"
            doc["text"] += metadata_text

        return [Document(page_content=doc['text']) for doc in docs]

    def perform_hybrid_search(self, query):
        # start_time = time.time()
        query_vector = self.embeddings.embed_query(query)
        # end_time = time.time()
        # print(end_time-start_time)
        # start_time = time.time()
        vector_results = self.collection.aggregate([
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
                "$project": {
                    "_id": 1,
                    "text": 1,
                    "url": 1,
                    "time": 1,
                    "vs_score": {
                        "$divide": [1.0, {"$add": [{"$indexOfArray": [None, "$_id"]}, self.vector_penalty, 1]}]
                    }
                }
            }
        ])
        # end_time = time.time()
        # print(end_time-start_time)

        full_text_results = self.collection.aggregate([
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
                "$project": {
                    "_id": 1,
                    "text": 1,
                    "url": 1,
                    "time": 1,
                    "fts_score": {
                        "$divide": [1.0, {"$add": [{"$indexOfArray": [None, "$_id"]}, self.full_text_penalty, 1]}]
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

        sorted_results = sorted(combined_results, key=lambda x: x['score'], reverse=True)[:self.limit]
        return sorted_results


if __name__ == "__main__":
    from pymongo import MongoClient
    from dotenv import load_dotenv
    import os
    import time

    load_dotenv()

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=256)

    client = MongoClient(os.getenv("MONGO_CONN"))
    db_name = "today"
    collection_name = "crawl"
    atlas_collection = client[db_name][collection_name]

    retriever = MongoHybridRetriever(
        collection=atlas_collection, 
        embeddings=embeddings
    )

    start_time = time.time()
    docs = retriever._get_relevant_documents("who is Arvind Narayanan?")
    end_time = time.time()
    for doc in docs:
        print("\n==================\n")
        print(doc)
    print("\nTime taken:", end_time - start_time, "seconds")
