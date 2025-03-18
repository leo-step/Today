import requests 
from bs4 import BeautifulSoup
import logging
from collections import deque
import time
from urllib.parse import urljoin, urlparse, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from tqdm import tqdm
import datetime
import pandas as pd
import hashlib
from pymongo import MongoClient
from langchain_text_splitters import HTMLSectionSplitter
import os
import re # stolen from populate.py
from dotenv import load_dotenv
load_dotenv()

client = MongoClient("mongodb+srv://shreyas:MONGOCLIENT_PASSWORD@cluster0.jx6ja.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
visited = set()
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
})
dataframe = pd.DataFrame(columns=['time', 'url', 'content', 'hashed_content'])
dataframe.index.name = 'website_url'
curr_page = 0
fWrite = open('visited.txt', 'w')
fRead = open('visited.txt', 'r')
duplicateCount = 0

# Chunking stuff

text_splitter = HTMLSectionSplitter(headers_to_split_on=[("h1", "Header 1"), ("h2", "Header 2")])


def load_previous_links():
    try:
        visited = set(fRead.read().splitlines())
    except FileNotFoundError:
        return set()

def cache_link(link):
    fWrite.write(link +'\n')

def get_hash(s):
    return hashlib.sha256(s.encode()).hexdigest()

def process_url(currUrl, timeout=5):
    global curr_page 
    global duplicateCount
    curr_page += 1
    try:
        # Get the page content
        print("Crawling", currUrl, "at time", datetime.datetime.now())
        print("Curr page", curr_page)
        response = session.get(currUrl, timeout=timeout)
        print("response headers", response.headers)
        links = get_links(currUrl, response, 'princeton.edu')
        soup = BeautifulSoup(response.text, features='html.parser')
        hash = get_hash(response.text)
        text = soup.get_text(separator=' ', strip=True)
        cache_link(currUrl)
        
        # Extract and process new links
        
        for link in tqdm(links):
            if link in visited: 
                duplicateCount += 1
            if 'princeton.edu' in link and link not in visited:
                print("Adding", link, "to queue")
                queue.append(link)
                visited.add(link)
            
        
        return currUrl, text, hash

    except requests.RequestException as e:
        logging.error("Failed to crawl", currUrl, e)
        return [], [], []
    except TimeoutError:
        return [], [], []
        pass  # Silently ignore timeout error


def remove_fragment(url):
    parsed_url = urlparse(url)
    return urlunparse((parsed_url.scheme, parsed_url.netloc, 
        parsed_url.path, parsed_url.params, parsed_url.query, ''))

def get_links(url, response, allowed_domain):
    try:
        print("Getting links from", url, "at time", datetime.datetime.now())
        soup = BeautifulSoup(response.text, features='lxml')
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
        links = [remove_fragment(link) for link in links]
        links = list(set(links))
        
        # Filter links to keep only those within the allowed domain
        links = [link for link in links if allowed_domain in urlparse(link).netloc]
        
        print(f"[INFO] Extracted {len(links)} links from {url}")
        return links
    except requests.RequestException as e:
        print(f"[ERROR] Failed to retrieve {url}: {e}")
        return []

def collapse_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()

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
                doc_id = get_hash(chunk.page_content)
                if doc_id not in self.id_set:
                    ids.append(doc_id)
                    documents.append(chunk)
                    self.id_set.add(doc_id)
            return count

    except Exception as e:
        print(f"[ERROR] couldn't populate with item {item}: {e}")
    

def crawl(queue, num_workers, max_pages):
    global duplicateCount
    while queue: 
        # Submit tasks for multiple URLs
        max_workers = 15
        worker_amt = min(max_workers, len(queue))
        total_amount = len(queue)
        next_batch = set([queue.popleft() for _ in range(worker_amt)])
        while total_amount > 0 and curr_page < max_pages: 
            with ThreadPoolExecutor(max_workers=len(next_batch)) as executor:
                futures = dict()
                for url in tqdm(next_batch): 
                    futures[url] = executor.submit(process_url, url)
                    print("futures[url] is", futures[url])
                time.sleep(0.1)
                print("Done with level of web crawling at time", datetime.datetime.now())
                print("Crawled", len(futures), "URLs")

                for future in as_completed(futures.values()):
                    result = future.result()
                    print("result[0] is", result[0], "result[1] is", result[1], "result[2] is", result[2])
                    dataframe.loc[curr_page] = pd.Series({
                        'time': datetime.datetime.now(),
                        'url': result[0],
                        'content': str(result[1]),  # Ensure it's a string
                        'hashed_content': str(result[2])  # Ensure it's a string
                    })

                print("total_amount", total_amount)
                print("curr_page", curr_page)
                            
                    
                total_amount -= len(next_batch)
                print("total amount left is", total_amount)
                
            
load_previous_links()

queue = deque(["http://princeton.edu"])
num_workers = 5 
max_pages = 10000
num_pages_crawled = crawl(queue, num_workers, max_pages)

print("duplicateCount", duplicateCount)
print("URLS", visited)

dataframe.to_csv("data.csv", index=False)
fWrite.close()
fRead.close()
