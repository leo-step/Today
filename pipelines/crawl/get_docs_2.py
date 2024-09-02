import os
import uuid
import asyncio
import aiohttp
from tqdm import tqdm

INPUT_PATH = "all_urls.txt"
OUTPUT_PATH = "./documents"
MAPPING_FILE = "crawl_index_mapping.txt"

with open(INPUT_PATH, "r") as file:
    urls = [line.strip() for line in file if line.strip()]
    urls = list(set(urls))
    urls = list(filter(lambda x: "dataspace" not in x, urls))
    print(len(urls))

# Set timeout settings
TIMEOUT = aiohttp.ClientTimeout(total=1)  # Set total timeout in seconds (adjust as needed)

async def fetch_html(session, url):
    """Fetch HTML content of a given URL with timeout."""
    try:
        async with session.get(url, timeout=TIMEOUT) as response:
            response.raise_for_status()
            return {'url': url, 'text': await response.text()}
    except Exception as e:
        # print(f"Error fetching {url}: {e}")
        return {'url': url, 'text': None}

async def fetch_all_html(urls):
    """Fetch HTML content for all URLs concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_html(session, url) for url in urls]
        return await asyncio.gather(*tasks)

def save_results(results):
    """Save HTML content to files and create a UUID-to-URL mapping."""
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    
    with open(MAPPING_FILE, 'a') as mapping_file:
        for result in results:
            try:
                url, text = result['url'], result['text']
                if text:
                    file_id = uuid.uuid4()
                    mapping_file.write(f"{file_id},{url}\n")
                    output_file = f'{OUTPUT_PATH}/{file_id}.html'
                    with open(output_file, 'w') as file:
                        file.write(text)
            except Exception as e:
                print(f"Couldn't write file for {url}: {e}")

def main():
    BATCH_SIZE = 100
    for i in tqdm(range(0, len(urls), BATCH_SIZE)):
        batch_urls = urls[i:i + BATCH_SIZE]
        results = asyncio.run(fetch_all_html(batch_urls))
        save_results(results)

if __name__ == "__main__":
    main()
