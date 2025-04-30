

import requests 
from bs4 import BeautifulSoup
import logging
from collections import deque
import time
from urllib.parse import urljoin, urlparse, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
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
timeoutDomains = dict()
session = requests.Session()
adapter = HTTPAdapter(pool_connections=50, pool_maxsize=50, max_retries=Retry(total=3))
session.mount("http://", adapter)
session.mount("https://", adapter)
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
})

dataframe = pd.DataFrame(columns=['time', 'url', 'content', 'hashed_content'])
dataframe.index.name = 'website_url'
curr_page = 0
fWrite = open('visited.txt', 'w')
fTime = open('times.txt', 'w')
fRead = open('visited.txt', 'r')
fTimeout = open('timedoutdomains.txt', 'w')


def load_previous_links():
    try:
        visited = set(fRead.read().splitlines())
    except FileNotFoundError:
        return set()

def cache_link(link):
    fWrite.write(link + "\n")

def get_hash(s):
    return hashlib.sha256(s.encode()).hexdigest()

def extract_text_with_inline_tags(soup):
    output = []
    index = 0
    raw_text = soup.get_text(separator=" ", strip=True)  # Preserve all text

    for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]):
        tag_start = f"<{element.name}>"  # Opening tag
        tag_end = f"</{element.name}>"  # Closing tag
        element_text = element.get_text(strip=True)  # Extract text inside the tag

        if element_text:
            # Find where this element’s text appears in the raw text
            pos = raw_text.find(element_text, index) # Can be optimized
            if pos != -1:
                # Insert the tag before the element
                raw_text = raw_text[:pos] + tag_start + element_text + tag_end + raw_text[pos + len(element_text):]
                index = pos + len(tag_start) + len(element_text) + len(tag_end)  # Move index forward

    return raw_text

def process_url(currUrl, timeout=15):
    global curr_page
    try:
        fTime.write("SUCCESS: request to " + currUrl + " at time " + str(datetime.datetime.now()) + "\n")
        response = session.get(currUrl, timeout=timeout)
        links = get_links(currUrl, response, 'princeton.edu')
        if len(links) == 0: 
            return [], [], []
        soup = BeautifulSoup(response.text, features='html.parser')

        text = extract_text_with_inline_tags(soup)
        time.sleep(0.01)
        print("SUCCESS:", currUrl)
        for link in tqdm(links):
            if 'princeton.edu' in link and (remove_formatting(link) not in visited):
                visited[remove_formatting(link)] = False
                queue.append(link)
                
        visited[remove_formatting(currUrl)] = True
        curr_page += 1
        return currUrl, text, hash

    except requests.RequestException as e:
        fTime.write("FAIL: request to " + currUrl + " at time " + str(datetime.datetime.now()) + "\n")
        logging.error("FAIL: %s %s", currUrl, e)
        if remove_formatting(currUrl) not in visited:
            visited[remove_formatting(currUrl)] = False
            queue.append(currUrl)
        return [], [], []    

def remove_fragment(url):
    parsed_url = urlparse(url)
    return urlunparse((parsed_url.scheme, parsed_url.netloc, 
        parsed_url.path, parsed_url.params, parsed_url.query, ''))

def remove_formatting(url: str) -> str:
    return url.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")

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

def validUrl(url, queue):
    if parseDomain(url) in timeoutDomains and timeoutDomains[parseDomain(url)] > 2:
        return False
    return not visited[remove_formatting(url)] and len(queue) >= 0
def crawl(queue, num_workers, max_pages):
    global visited
    global curr_page
    while queue and curr_page < max_pages: 
        # Submit tasks for multiple URLs
        worker_amt = min(num_workers, len(queue))
        total_amount = len(queue)
        next_batch = []
        while len(next_batch) < worker_amt and queue:
            url = queue.popleft()
            if validUrl(url, queue):
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
                        'content': str(result[1]),  # Ensure it's a string
                        'hashed_content': str(result[2])  # Ensure it's a string
                        })
                        print("Adding", result[0], "to data.")
                    if (curr_page % 100 == 0):
                        dataframe.to_csv("data.csv", index=True)
                    cache_link(str(result[0]))
                except Exception as e:
                    print(f"Error processing {url}: {e}")
            visited[remove_formatting(str(result[0]))] = True  
            total_amount -= len(next_batch)
                

queue = deque(["http://princeton.edu"])
visited[remove_formatting("http://princeton.edu")] = False
num_workers = 30
max_pages = 100000
num_pages_crawled = crawl(queue, num_workers, max_pages)
fTimeout.writelines(str(_) + "\n" for _ in timeoutDomains)
fWrite.close()
fTime.close()
fTimeout.close()
fRead.close()

