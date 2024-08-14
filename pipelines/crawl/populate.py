from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from langchain_text_splitters import HTMLSectionSplitter
from dotenv import load_dotenv
from sqlalchemy.exc import ProgrammingError
import hashlib
import os
import re
import time

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"
collection_name = "crawl_chunks"

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
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


if __name__ == "__main__":
    is_dry_run = False
    OUTPUT_PATH = "./documents"
    uuid_url_mapping = build_crawl_index_url_map()

    count = 0
    for filename in os.listdir(OUTPUT_PATH):
        file_path = os.path.join(OUTPUT_PATH, filename)
        uuid = os.path.splitext(filename)[0]
        if uuid not in uuid_url_mapping:
            continue # ??
        with open(file_path) as f:
            doc_text = f.read()
            chunks = text_splitter.split_text(doc_text)
            documents = []

            for chunk in chunks:
                if "UltraDNS" in chunk.page_content:
                    continue # lol
                chunk.page_content = collapse_whitespace(chunk.page_content)
                chunk.metadata = {
                    "id": sha256_hash_string(chunk.page_content), 
                    "url": uuid_url_mapping[uuid],
                    "time": int(time.time())
                }
                documents.append(chunk)
            
            if not is_dry_run:
                try:
                    vector_store.add_documents(documents, ids=[doc.metadata["id"] for doc in documents])
                except ProgrammingError:
                    print("[WARN] encountered cardinality violation, inserting chunks one by one")
                    for doc in documents:
                        vector_store.add_documents([doc], ids=[doc.metadata["id"]])
                count += len(documents)
                print(f"[INFO] added {len(documents)} documents to vector store")
            else:
                print(f"[INFO] processed {len(documents)} documents in dry run")

    print(f"[INFO] finished with count = {count} (potential duplicates included)")
