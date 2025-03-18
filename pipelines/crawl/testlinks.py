import requests
from bs4 import BeautifulSoup

response = requests.get("https://www.princeton.edu/research/social-sciences", timeout=2)
assert(response.status_code == 200)
soup = BeautifulSoup(response.text, 'html.parser')
text = str(soup)
print(text)