from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import hashlib
import os

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

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=128,
    length_function=len,
    is_separator_regex=False,
)

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


if __name__ == "__main__":
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
            chunks = text_splitter.create_documents([doc_text])
            for chunk in chunks:
                chunk.metadata = {
                    "id": sha256_hash_string(chunk.page_content), 
                    "url": uuid_url_mapping[uuid]
                }
            vector_store.add_documents(chunks, ids=[doc.metadata["id"] for doc in chunks])
            count += len(chunks)
            print(f"[INFO] added {len(chunks)} documents to vector store")

    print(f"[INFO] Finished with count = {count}")
