import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import threading
import os

MAX_DEPTH = 12

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

def crawl(url, depth, visited_links, lock, executor, allowed_domain, file):
    if depth > MAX_DEPTH:
        return
    
    with lock:
        if url in visited_links:
            return
        visited_links.add(url)
    
    links = get_links(url, allowed_domain)
    
    with open(file, "a") as fp:
        for link in links:
            with lock:
                if link not in visited_links:
                    fp.write(link + '\n')
    
    # Print the current depth and number of new links being crawled
    print(f"[INFO] Crawling depth {depth}: {len(links)} links found on {url}")
    
    # Submit tasks for each link to be crawled in parallel
    futures = [executor.submit(crawl, link, depth + 1, visited_links, lock, executor, allowed_domain, file) for link in links]

    # Wait for all tasks to complete with timeout
    try:
        for future in as_completed(futures, timeout=15):
            try:
                future.result(timeout=10)  # Timeout for individual tasks
            except TimeoutError:
                print("[ERROR] A task timed out.")
            except Exception as e:
                print(f"[ERROR] An error occurred: {e}")
    except TimeoutError:
        print("[ERROR] Timeout waiting for futures to complete. Continuing with the next batch...")

def run_crawler_on_urls(input_file):
    if not os.path.exists("urls_out"):
        os.makedirs("urls_out")  # Create output directory if it doesn't exist

    with open(input_file, "r") as f:
        base_urls = [line.strip() for line in f.readlines()]
    
    lock = threading.Lock()  # Lock for thread-safe access to shared resources
    visited_links = set()
    # Create a ThreadPoolExecutor to manage threads across multiple base URLs
    with ThreadPoolExecutor(max_workers=64) as executor:
        futures = []
        for i, base_url in enumerate(base_urls):
            allowed_domain = "princeton.edu"  # Domain restriction
            
            output_file = f"urls_out/{i}.txt"

            with open(output_file, "w") as fp:
                fp.write(base_url + '\n')

            # Submit the crawl task for each base URL
            print(f"[INFO] Starting crawl at {base_url} within domain {allowed_domain}")
            future = executor.submit(crawl, base_url, 1, visited_links, lock, executor, allowed_domain, output_file)
            futures.append(future)

        # Wait for all futures to complete
        for future in as_completed(futures):
            try:
                future.result()  # Retrieve the result to raise any exceptions
            except Exception as e:
                print(f"[ERROR] An error occurred during crawling: {e}")

    print("[INFO] Crawling completed for all base URLs. DONE")

if __name__ == "__main__":
    input_file = "urls.txt"  # File containing base URLs
    run_crawler_on_urls(input_file)
