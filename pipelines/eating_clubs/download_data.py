import requests
from bs4 import BeautifulSoup
import os

# Function to download and save HTML page
def download_html(url, save_directory):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Check for request errors
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get a clean file name from the URL
        file_name = url.replace('https://', '').replace('http://', '').replace('/', '_') + '.html'
        file_path = os.path.join(save_directory, file_name)
        
        # Write the prettified HTML to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"Saved: {url} -> {file_path}")
    
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")

# Function to read links from a text file and download each HTML page
def download_html_from_file(links_file, save_directory):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    with open(links_file, 'r') as file:
        links = file.readlines()
    
    for link in links:
        url = link.strip()
        if url:
            download_html(url, save_directory)

if __name__ == "__main__":
    # Input text file with links (one per line)
    links_file = 'eating_clubs/urls.txt'
    
    # Directory to save the downloaded HTML files
    save_directory = 'eating_clubs/data'
    
    # Download HTML pages
    download_html_from_file(links_file, save_directory)
