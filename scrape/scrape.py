import pymongo
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup

load_dotenv()
client = pymongo.MongoClient(os.getenv("DB_CONN"))
db = client.data

def get_weather():
    weatherPton = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?lat=40.343899&lon=-74.660049&appid={os.getenv("WEATHER")}&units=imperial').json()
    weatherPton['_id'] = 'weather'
    return weatherPton

def get_menus():
    dining_halls = {
        "Whitman College": 8,
        "Butler College": 2,
        "Rockefeller and Mathey Colleges": 1,
        "Forbes College": 3,
        "Center for Jewish Life": 5,
        "Yeh West College": 6
    }
    result = {}
    for dhall, index in dining_halls.items():
        dhall_result = {}
        url = "https://menus.princeton.edu/dining/_Foodpro/online-menu/menuDetails.asp?locationNum={:02d}".format(index)
        text = requests.get(url).text
        soup = BeautifulSoup(text, features="lxml")
        menus = soup.findAll("div", {"class" : "card mealCard"})
        
        for menu in menus:
            text = menu.text.replace("Nutrition", '').replace('\r', '')
            items = [item.strip() for item in text.split("\n") if item.strip()]
            subitems = {}
            category = None
            for i in range(1, len(items)):
                if items[i][0] == '-':
                    key = items[i].replace('-- ', '').replace(' --', '')
                    subitems[key] = []
                    category = key
                else:
                    subitems[category].append(items[i])
            dhall_result[items[0]] = subitems
        result[dhall] = dhall_result
    result["_id"] = "dhall"
    return result

def get_prince():
    url = "https://www.dailyprincetonian.com/"
    text = requests.get(url).text
    soup = BeautifulSoup(text, features="lxml")
    articles = list(soup.find("h1", {"class" : "headline"}))

    articles.append(soup.findAll("h2", {"class" : "headline"}))

    print(articles)




    return {
     
        
     
     
        # "_id": "prince",
        # "articles": [
        #     {"title": "After visual arts professor used n-word in seminar, Princeton finds no violation of policy", "link": "/"},
        #     {"title": "Fintan O’Toole warns of the danger of ‘aestheticized politics’ in campus talk", "link": "/"},
        #     {"title": "University officially announces new upperclass student dining pilot", "link": "/"}
        # ]
    }

# db.widgets.replace_one({"_id": "weather"}, get_weather(), True)
# db.widgets.replace_one({"_id": "dhall"}, get_menus(), True)
# db.widgets.replace_one({"_id": "prince"}, get_prince(), True)

get_prince()