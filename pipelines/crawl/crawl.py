import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import threading

MAX_DEPTH = 2

def remove_fragment(url):
    parsed_url = urlparse(url)
    return urlunparse((parsed_url.scheme, parsed_url.netloc, 
        parsed_url.path, parsed_url.params, parsed_url.query, ''))

def get_links(url, allowed_domain):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, features='lxml')
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
        links = [remove_fragment(link) for link in links]
        links = list(set(links))
        
        # Filter links to keep only those within the allowed domain
        links = [link for link in links if urlparse(link).netloc.endswith(allowed_domain)]
        
        print(f"[INFO] Extracted {len(links)} links from {url}")
        return links
    except requests.RequestException as e:
        print(f"[ERROR] Failed to retrieve {url}: {e}")
        return []

def crawl(url, depth, visited_links, lock, executor, allowed_domain):
    if depth > MAX_DEPTH:
        return
    
    with lock:
        if url in visited_links:
            return
        visited_links.add(url)
    
    links = get_links(url, allowed_domain)
    
    with open("urls.txt", "a") as fp:
        for link in links:
            with lock:
                if link not in visited_links:
                    fp.write(link + '\n')
    
    # Print the current depth and number of new links being crawled
    print(f"[INFO] Crawling depth {depth}: {len(links)} links found on {url}")
    
    # Submit tasks for each link to be crawled in parallel
    futures = [executor.submit(crawl, link, depth + 1, visited_links, lock, executor, allowed_domain) for link in links]

    # Wait for all tasks to complete with timeout
    try:
        for future in as_completed(futures, timeout=60):
            try:
                future.result(timeout=60)  # Timeout for individual tasks
            except TimeoutError:
                print("[ERROR] A task timed out.")
            except Exception as e:
                print(f"[ERROR] An error occurred: {e}")
    except TimeoutError:
        print("[ERROR] Timeout waiting for futures to complete. Continuing with the next batch...")

if __name__ == "__main__":
    base_url = "https://www.princeton.edu/"
    allowed_domain = "princeton.edu"  # Domain restriction
    visited_links = set()
    lock = threading.Lock()  # Lock for thread-safe access to shared resources
    
    with open("urls.txt", "w") as fp:
        fp.write(base_url + '\n')
    
    # Create a ThreadPoolExecutor to manage threads
    with ThreadPoolExecutor(max_workers=10) as executor:
        print(f"[INFO] Starting crawl at {base_url} within domain {allowed_domain}")
        crawl(base_url, 1, visited_links, lock, executor, allowed_domain)
        print("[INFO] Crawling completed.")
