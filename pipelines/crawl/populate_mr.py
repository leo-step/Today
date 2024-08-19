# parallel version of populate.py

from langchain_openai import OpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_text_splitters import HTMLSectionSplitter
from pymongo import MongoClient
from dotenv import load_dotenv
from mr import MapReduce
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
# atlas_collection.delete_many({})
vector_search_index = "vector_index"

vector_store = MongoDBAtlasVectorSearch(
    atlas_collection,
    embeddings
)

text_splitter = HTMLSectionSplitter(headers_to_split_on=[("h1", "Header 1"), ("h2", "Header 2")])

def sha256_hash_string(input_string):
    encoded_string = input_string.encode()
    sha256_hash = hashlib.sha256()
    sha256_hash.update(encoded_string)
    return sha256_hash.hexdigest()

def build_crawl_index_url_map():
    MAPPING_PATH = "crawl_index_mapping.txt"
    uuid_url_mapping = {}

    with open(MAPPING_PATH, 'r') as file:
        for line in file:
            uuid, url = line.strip().split(',')
            uuid_url_mapping[uuid] = url
    
    return uuid_url_mapping

def collapse_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()


class PopulateJob(MapReduce):
    def get_items(self):
        self.is_dry_run = False
        self.OUTPUT_PATH = "./documents"
        self.uuid_url_mapping = build_crawl_index_url_map()
        self.id_set = set()
        return os.listdir(self.OUTPUT_PATH)

    def mapF(self, item):
        try:
            filename = item
            file_path = os.path.join(self.OUTPUT_PATH, filename)
            uuid = os.path.splitext(filename)[0]
            if uuid not in self.uuid_url_mapping:
                return 0
            with open(file_path) as f:
                count = 0
                doc_text = f.read()
                chunks = text_splitter.split_text(doc_text)
                documents = []
                ids = []
                for chunk in chunks:
                    if "UltraDNS" in chunk.page_content:
                        continue # lol
                    chunk.page_content = collapse_whitespace(chunk.page_content)
                    chunk.metadata = {
                        "links": [self.uuid_url_mapping[uuid]],
                        "time": int(time.time())
                    }
                    doc_id = sha256_hash_string(chunk.page_content)
                    if doc_id not in self.id_set:
                        ids.append(doc_id)
                        documents.append(chunk)
                        self.id_set.add(doc_id)
                
                if not self.is_dry_run:
                    vector_store.add_documents(documents, ids=ids)
                    count += len(documents)
                #     print(f"[INFO] added {len(documents)} documents to vector store")
                # else:
                #     print(f"[INFO] processed {len(documents)} documents in dry run")
                return count

        except Exception as e:
            print(f"[ERROR] couldn't populate with item {item}: {e}")
    
    def reduceF(self, results):
        print(f"[INFO] finished with count = {sum(results)}")


if __name__ == "__main__":
    job = PopulateJob()
    job.run()