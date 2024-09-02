from mr import MapReduce
import requests
from bs4 import BeautifulSoup
import os
import uuid

INPUT_PATH = "all_urls.txt"
OUTPUT_PATH = "./documents"
MAPPING_PATH = "crawl_index_mapping.txt"

class MakeData_Job(MapReduce):
    def __init__(self, urls, mapping_file):
        super().__init__()
        self.urls = list(set(urls))
        self.mapping_file = mapping_file

    def get_items(self):
        print("NUM URLS:", len(self.urls))
        return self.urls
    

    def mapF(self, url):
        try:
            response = requests.get(url, timeout=2)
            assert(response.status_code == 200)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = str(soup)
            return {'url': url, 'text': text}
        except Exception as e:
            pass
        return {'url': url, 'text': None}


    def reduceF(self, results):
        if not os.path.exists(OUTPUT_PATH):
            os.makedirs(OUTPUT_PATH)
        
        for result in results:
            try:
                url, text = result['url'], result['text']
                if text:
                    id = uuid.uuid4()
                    self.mapping_file.write(f"{id},{url}\n")
                    output_file = f'{OUTPUT_PATH}/{id}.html'
                    with open(output_file, "w") as file:
                        file.write(text)
            except:
                print("Couldn't write file")

def batch_iterate(data, batch_size):
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

if __name__ == '__main__':
    with open(INPUT_PATH, "r") as file:
        urls = [line.strip() for line in file if line.strip()]
        
        if os.path.exists(MAPPING_PATH):
            os.remove(MAPPING_PATH)

        with open(MAPPING_PATH, "a") as mapping_file:
            for batch in batch_iterate(urls, 512):
                job = MakeData_Job(batch, mapping_file)
                job.run(num_workers=64)
    