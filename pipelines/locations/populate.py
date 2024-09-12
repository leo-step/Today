from langchain_openai import OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pymongo import MongoClient
from dotenv import load_dotenv
import hashlib
import os
import re
import time

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-large", dimensions=256)

client = MongoClient(os.getenv("MONGO_CONN"))
# Define collection and index name
db_name = "today"
collection_name = "crawl"
atlas_collection = client[db_name][collection_name]
vector_search_index = "vector_index"

vector_store = MongoDBAtlasVectorSearch(
    atlas_collection,
    embeddings
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=8096,
    chunk_overlap=0,
    length_function=len,
    is_separator_regex=False,
)

def sha256_hash_string(input_string):
    encoded_string = input_string.encode()
    sha256_hash = hashlib.sha256()
    sha256_hash.update(encoded_string)
    return sha256_hash.hexdigest()

def collapse_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()


if __name__ == "__main__":
    is_dry_run = False
    OUTPUT_PATH = "locations/data"

    count = 0
    id_set = set()
    for filename in os.listdir(OUTPUT_PATH):
        file_path = os.path.join(OUTPUT_PATH, filename)
        uuid = os.path.splitext(filename)[0]
        with open(file_path) as f:
            doc_text = f.read()
            page_contents = text_splitter.split_text(doc_text)
            documents = []
            ids = []
            for content in page_contents:
                chunk = Document(page_content=collapse_whitespace(content))
                chunk.metadata = {
                    "links": [],
                    "time": int(time.time()),
                    "source": "map"
                }
                doc_id = sha256_hash_string(chunk.page_content)
                if doc_id not in id_set:
                    ids.append(doc_id)
                    documents.append(chunk)
                    id_set.add(doc_id)
            
            if not is_dry_run:
                vector_store.add_documents(documents, ids=ids)
                count += len(documents)
                print(f"[INFO] added {len(documents)} documents to vector store")
            else:
                print(f"[INFO] processed {len(documents)} documents in dry run")

    print(f"[INFO] finished with count = {count}")
