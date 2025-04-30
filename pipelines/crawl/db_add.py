from pymongo import MongoClient
import pandas as pd
import logging
from datetime import datetime
import os
from langchain_text_splitters import HTMLSectionSplitter
from langchain_mongodb import MongoDBAtlasVectorSearch
import datetime as time
import re

client = MongoClient("mongodb+srv://shreyas:MONGOCLIENT_PASSWORD@cluster0.jx6ja.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

text_content = dict()
df = None
db = client['todaycrawl']
col = db['princetoncrawl']
atlas_collection = client['todaycrawl']['princetoncrawl']

text_splitter = HTMLSectionSplitter(headers_to_split_on=[("h1", "Header 1"), 
                                                         ("h2", "Header 2"),
                                                         ("h3", "Header 3"),
                                                         ("h4", "Header 4"),
                                                         ("h5", "Header 5"),
                                                         ("h6", "Header 6"),
                                                         ("p", "Paragraph"),
                                                         ("li", "List"),
                                                         ])

def collapse_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()

def chunk_text(text, max_length=1000):
    """Split text into smaller chunks of max_length."""
    chunks = []
    for i in range(0, len(text), max_length):
        chunks.append(text[i:i + max_length])
    return chunks

def add_document(url, doc_text, hash, date):
    try:
        existing_doc = atlas_collection.find_one({"metadata.url": url})
        
        if existing_doc:
            print(f"[INFO] Document with URL {url} already exists. Removing the old document.")
            # Remove the existing document with the same URL
            atlas_collection.delete_many({"metadata.url": url})
        
        count = 0
        # Split document into sections first
        sections = text_splitter.split_text(doc_text)
        
        # Now split each section further if necessary (into chunks of max 1000 characters)
        for section in sections:
            if "UltraDNS" in section.page_content:
                continue  # Skip this section if it contains "UltraDNS"
            
            section.page_content = collapse_whitespace(section.page_content)

            # Split section into smaller chunks if it's too large
            chunks = chunk_text(section.page_content)

            for chunk in chunks:
                # Create metadata for the chunk
                chunk_metadata = {
                    "url": url,
                    "time uploaded": str(datetime.now()),
                    "num_chars": len(chunk)
                }
                
                # Insert chunk into the database
                chunk_dict = {
                    "content": chunk,
                    "metadata": chunk_metadata
                }
                atlas_collection.insert_one(chunk_dict)
                count += 1

        print(f"[INFO] added {count} documents to vector store")
        return count

    except Exception as e:
        print(f"[ERROR] couldn't populate with url {url}: {e}")

def load_content(): 
    global df
    df = pd.read_csv("data.csv")
    for index, row in df.iterrows():
        try:
            count = add_document(str(row['url']), str(row['content']), str(row['hashed_content']), str(index))
            if count: 
                print(f"[INFO] finished with count = {count}")
        except Exception as e:
            logging.error("Failed to add: %s at time %s with error %s", str(row['url']), str(datetime.now()), str(e))

load_content()