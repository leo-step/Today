from mr import MapReduce
import requests
from bs4 import BeautifulSoup
import os
import uuid

INPUT_PATH = "urls.txt"
OUTPUT_PATH = "./documents"
MAPPING_PATH = "crawl_index_mapping.txt"

class MakeData_Job(MapReduce):
    def get_items(self):
        with open(INPUT_PATH, "r") as file:
            urls = [line.strip() for line in file if line.strip()][:100]
        print("NUM URLS:", len(set(urls)))
        return list(set(urls))
    

    def mapF(self, url):
        try:
            response = requests.get(url)
            assert(response.status_code == 200)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator="\n", strip=True)
            return {'url': url, 'text': text}
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return {'url': url, 'text': None}


    def reduceF(self, results):
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)
        if os.path.exists(MAPPING_PATH):
            os.remove(MAPPING_PATH)
        
        for result in results:
            try:
                url, text = result['url'], result['text']
                if text:
                    id = uuid.uuid4()
                    with open(MAPPING_PATH, "a") as file:
                        file.write(f"{id},{url}\n")
                    output_file = f'{OUTPUT_PATH}/{id}.txt'
                    with open(output_file, "w") as file:
                        file.write(text)
            except:
                print("Couldn't write file")


if __name__ == '__main__':
    job = MakeData_Job()
    job.run(num_workers=16)