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
import threading

load_dotenv()
lock = threading.Lock()

client = MongoClient("mongodb+srv://shreyas:MONGOCLIENT_PASSWORD@cluster0.jx6ja.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
visited = dict()
linksNoProtocol = set()
timeoutDomains = dict()
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
})

dataframe = pd.DataFrame(columns=['time', 'url', 'content', 'hashed_content'])
dataframe.index.name = 'website_url'
curr_page = 0
fWrite = open('visited.txt', 'w')
fWrite2 = open('currUrl.txt', 'w')
fWrite3 = open('times.txt', 'w')
fRead = open('visited.txt', 'r')

# Chunking stuff

text_splitter = HTMLSectionSplitter(headers_to_split_on=[("h1", "Header 1"), ("h2", "Header 2")])

def load_previous_links():
    try:
    
        visited = set(fRead.read().splitlines())
    except FileNotFoundError:
        return set()

def cache_link(link):
    fWrite.write(link + "\n")

def get_hash(s):
    return hashlib.sha256(s.encode()).hexdigest()

def process_url(currUrl, timeout=15):
    global curr_page
    try:
        fWrite3.write("SUCCESS: request to " + currUrl + " at time " + str(datetime.datetime.now()) + "\n")
        response = session.get(currUrl, timeout=timeout)
        links = get_links(currUrl, response, 'princeton.edu')
        if len(links) == 0: 
            return [], [], []
        soup = BeautifulSoup(response.text, features='html.parser')
        hash = get_hash(response.text)
        text = soup.get_text(separator=' ', strip=True)
        time.sleep(0.01)
        print("SUCCESS:", currUrl)
        for link in tqdm(links):
            if 'princeton.edu' in link and (link not in visited):
                visited[link] = False
                queue.append(link)
                
        visited[currUrl] = True
        curr_page += 1
        return currUrl, text, hash

    except requests.RequestException as e:
        fWrite3.write("FAIL: request to " + currUrl + " at time " + str(datetime.datetime.now()) + "\n")
        logging.error("FAIL: %s %s", currUrl, e)
        if currUrl not in visited:
            visited[currUrl] = False
            queue.append(currUrl)
        return [], [], []

    

def remove_fragment(url):
    parsed_url = urlparse(url)
    return urlunparse((parsed_url.scheme, parsed_url.netloc, 
        parsed_url.path, parsed_url.params, parsed_url.query, ''))

def remove_https(url: str) -> str:
    return url.replace("https://", "").replace("http://", "")

def get_links(url, response, allowed_domain):
    try:
        soup = BeautifulSoup(response.text, features='lxml')
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
        links = [remove_fragment(link) for link in links]
        links = list(set(links))

        excluded_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf', 
                               '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
                               '.zip', '.tar', '.gz', '.rar', '.mp3', '.mp4', '.avi', '.mov')
        
        # Filter links to keep only those within the allowed domain
        links = [link for link in links if allowed_domain in urlparse(link).netloc]
        links = [link for link in links if not link.lower().endswith(excluded_extensions)]
        return links
    except requests.RequestException as e:
        return []
    except TimeoutError:
        urlDomain = parseDomain(url)
        if timeoutDomains[urlDomain]:
            timeoutDomains[urlDomain] += 1
        else:
            timeoutDomains[urlDomain] = 1
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
        print("")
def parseDomain(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.netloc

def validUrl(url):
    if parseDomain(url) in timeoutDomains and timeoutDomains[parseDomain(url)] > 2:
        return False
    return not visited[url] and len(queue) >= 0
def crawl(queue, num_workers, max_pages):
    global visited
    global curr_page
    while queue and curr_page < 200000: 
        print(curr_page)
        # Submit tasks for multiple URLs
        max_workers = 25
        worker_amt = min(max_workers, len(queue))
        total_amount = len(queue)
        next_batch = []
        while len(next_batch) < worker_amt and queue:
            url = queue.popleft()
            if validUrl(url):
                next_batch.append(url)
        with ThreadPoolExecutor(max_workers=len(next_batch)) as executor:
            futures = dict()
            results = []
            for url in tqdm(next_batch): 
                futures[url] = executor.submit(process_url, url)
            for future in as_completed(futures.values()):
                try:
                    result = future.result()
                    results.append(result[0])
                    if len(result[0]) != 0:
                        dataframe.loc[curr_page] = pd.Series({
                        'time': datetime.datetime.now(),
                        'url': result[0],
                        'content': str(result[1][:200]),  # Ensure it's a string
                        'hashed_content': str(result[2])  # Ensure it's a string
                        })
                    if (curr_page % 100 == 0):
                        dataframe.to_csv("data.csv", index=False)
                    cache_link(str(result[0]))
                except Exception as e:
                    print(f"Error processing {url}: {e}")
            for url in results:
                fWrite2.write(str(url) + "\n")
            print("RESULTS ARE", results)
            print("ADDING TO SHEET")
                
            visited[str(result[0])] = True  
            # cache_link(str(result[0]))
            total_amount -= len(next_batch)
                

queue = deque(["http://example.com:81"])
visited["http://example.com:81"] = False
num_workers = 5 
max_pages = 30
# num_pages_crawled = crawl(queue, num_workers, max_pages)
print(remove_fragment("https://princeton.edu"))


#print("# leftover pages in queue", len(queue))
fWrite.close()
fWrite2.close()
fWrite3.close()
fRead.close()
