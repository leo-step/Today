import requests
import re
from bs4 import BeautifulSoup

CATEGORIES_URL = "https://m.princeton.edu/default/map/index.json"
PLACEMARKS_URL = "https://m.princeton.edu/default/map/index.json?feed=campus_map&parentId=campus_map%2F{}&_recenter=true&_maptab=browse&_kgoui_object=kgoui_Rcontent_I0_Rcenter_I0_RmapImpl_I0&_kgoui_js_config=1&_kgoui_navigation_state=9bde1c66596e61c0d98a9ba6802dc50c&_kgoui_nocache=1726165659435"
DETAILS_URL = "https://m.princeton.edu/default/map/index.json"

# Define the URL
url = "https://m.princeton.edu/default/map/index.json"

# Define the query parameters
params = {
    "_kgoui_region": "kgoui_Rcontent_I0_Rleft_I0_Rbrowse",
    "_kgoui_include_html": "1",
    "_kgoui_js_config": "1",
    "_kgoui_navigation_state": "9bde1c66596e61c0d98a9ba6802dc50c",
}

# Define the headers
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "_kgosession=552d6cf0e754bd6ecf1c10b9779d9eae; _kgouuid=e3729fd4-8e35-499e-a5f9-c2e41414d190; backend=dc2839bf0224585bf39659f416d8bd0d",
    "DNT": "1",
    "Host": "m.princeton.edu",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"'
}

# Send the GET request
response = requests.get(url, headers=headers, params=params).json()

# Print the response
text = response["response"]["html"]

pattern = r'"parentId":"campus_map\\/([^"]+)"'

# Search for the pattern in the text
matches = re.findall(pattern, text)

for match in matches:
    if match == "Accessible" or match == "Bluespot":
        continue
    print(match)
    response = requests.get(PLACEMARKS_URL.format(match), headers=headers, params=params).json()

    with open(f"locations/data/{match}.txt", "a") as fp:
        placemarks = response["response"]["fields"]["placemarks"]["value"]

        for i, placemark in enumerate(placemarks):
            print(i+1, "/", len(placemarks))
            urlargs = placemark["kgoDeflatedData"]["attributes"]["kgomap:urlargs"]

            url_params = {
                "_kgoui_region": "kgoui_Rcontent_I0_Rright",
                "_kgoui_include_html": "1",
                "_kgoui_js_config": "1",
                "_kgoui_navigation_state": "9bde1c66596e61c0d98a9ba6802dc50c",
                "feed": urlargs["feed"],
                "parentId": urlargs["parentId"],
                "_recenter": urlargs["_recenter"],
                "_maptab": urlargs["_maptab"],
                "id": urlargs["id"]
            }

            response = requests.get(DETAILS_URL, headers=headers, params=url_params).json()
            soup = BeautifulSoup(response["response"]["html"], features="lxml")
            fp.write(soup.text.split("Nearby tab content")[0])
            fp.write("============================\n")
