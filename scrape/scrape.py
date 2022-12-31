import pymongo
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup

load_dotenv()
client = pymongo.MongoClient(os.getenv("DB_CONN"))
db = client.data

def get_weather_daily():
    result = {}
    weatherDaily = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat=40.343899&lon=-74.660049&appid={os.getenv("WEATHER")}&units=imperial').json()
    result['current'] = round(weatherDaily['main']['temp'])
    result['min'] = round(weatherDaily['main']['temp_min'])
    result['max'] = round(weatherDaily['main']['temp_max'])
    return result

def get_weather():
    weatherPton = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?lat=40.343899&lon=-74.660049&appid={os.getenv("WEATHER")}&units=imperial').json()
    weatherPton['_id'] = 'weather'
    weatherPton['current_data'] = get_weather_daily()
    return weatherPton


def get_menus():
    dining_halls = {
        "Whitman": 8,
        "Wucox": 2,
        "Roma": 1,
        "Forbes": 3,
        "Center for Jewish Life": 5,
        "Yeh/NCW": 6
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
    articles = []
    url = "https://www.dailyprincetonian.com/"
    text = requests.get(url).text
    soup = BeautifulSoup(text, features="lxml")
    mainArticle = soup.find("h1", {"class" : "headline"})

    secondArticles = soup.findAll("h2", {"class" : "headline"})

    text1 = mainArticle.find('a').contents[0]
    link1 = mainArticle.find('a').get("href")

    text2 = secondArticles[0].find('a').contents[0]
    text3 = secondArticles[2].find('a').contents[0]

    link2 = secondArticles[0].find('a').get("href")
    link3 = secondArticles[2].find('a').get("href")

    articles.append({'title': text1, 'link': link1})
    articles.append({'title': text2, 'link': link2})
    articles.append({'title': text3, 'link': link3})


    return {

        "_id": "prince",
        "articles": articles

    }


db.widgets.replace_one({"_id": "weather"}, get_weather(), True)
db.widgets.replace_one({"_id": "dhall"}, get_menus(), True)
db.widgets.replace_one({"_id": "prince"}, get_prince(), True)

