from pymongo import MongoClient
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import os

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=256)

client = MongoClient(os.getenv("MONGO_CONN"))

db_name = "today"
collection_name = "crawl"
atlas_collection = client[db_name][collection_name]

query = "Arvind Narayanan"
query_vector = embeddings.embed_query(query)

vector_penalty = 1
full_text_penalty = 1
result = atlas_collection.aggregate([
  {
    "$vectorSearch": {
      "index": "vector_index",
      "path": "embedding",
      "queryVector": query_vector,
      "numCandidates": 100,
      "limit": 20
    }
  },
  {
    "$group": {
      "_id": None,
      "docs": { "$push": "$$ROOT" }
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
        "$divide": [1.0, { "$add": ["$rank", vector_penalty, 1] }]
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
          "$limit": 20
        },
        {
          "$group": {
            "_id": None,
            "docs": { "$push": "$$ROOT" }
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
                { "$add": ["$rank", full_text_penalty, 1] }
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
      "vs_score": { "$max": "$vs_score" },
      "fts_score": { "$max": "$fts_score" }
    }
  },
  {
    "$project": {
      "_id": 1,
      "text": 1,
      "vs_score": { "$ifNull": ["$vs_score", 0] },
      "fts_score": { "$ifNull": ["$fts_score", 0] }
    }
  },
  {
    "$project": {
      "score": { "$add": ["$fts_score", "$vs_score"] },
      "_id": 1,
      "text": 1,
      "vs_score": 1,
      "fts_score": 1
    }
  },
  {
    "$sort": { "score": -1 }
  },
  {
    "$limit": 10
  }
])

for doc in result:
    print(doc)