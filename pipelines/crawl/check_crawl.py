# check that crawl_index_mapping contains the urls we want

def build_crawl_index_url_map():
    MAPPING_PATH = "crawl_index_mapping.txt"
    uuid_url_mapping = {}

    with open(MAPPING_PATH, 'r') as file:
        for line in file:
            uuid, url = line.strip().split(',')
            uuid_url_mapping[uuid] = url
    
    return uuid_url_mapping

CRITICAL_URLS = [
    "https://www.princeton.edu/academics/career-development",
    "https://princetoneatingclubs.org/",
    "https://www.princeton.edu/news/2015/07/23/chew-examining-racial-identity-one-literary-bite-time?section=featured"
]

uuid_url_mapping = build_crawl_index_url_map()
urls = set(uuid_url_mapping.values())

for url in CRITICAL_URLS:
    if url not in urls:
        print(url, "not found in crawl")

print("done")