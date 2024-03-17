import pymongo
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

load_dotenv()
client = pymongo.MongoClient(os.getenv("DB_CONN"))
db = client[os.getenv("DATABASE")]

nightTimes = ['7 pm', '10 pm','1 am','4 am']
dateTime = {
    '00:00:00': '7 pm',
    '03:00:00': '10 pm',
    '06:00:00': '1 am',
    '09:00:00': '4 am',
    '12:00:00': '7 am',
    '15:00:00': '10 am',
    '18:00:00': '1 pm',
    '21:00:00': '4 pm'
}

def weatherEmoji(code, time):
    if code == 804:
        return '☁️'
    if code >= 800:
        if time in nightTimes:
            return '🌙'
        if code < 802:
            return '☀️'
        if code == 802:
            return '🌤'
        if code == 803:
            return '⛅️'
    if code < 300:
        return '🌩'
    elif code < 600:
        return '🌧'
    elif code < 700:
        return '❄️'
    elif code < 800:
        return '🌫'
    else:
        return '☀️'


def get_weather():
    weatherPton = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?lat=40.343899&lon=-74.660049&appid={os.getenv("WEATHER")}&units=imperial').json()
    weatherDaily = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat=40.343899&lon=-74.660049&appid={os.getenv("WEATHER")}&units=imperial').json()
    result = {
        'current': round(weatherDaily['main']['temp']),
        'min': round(weatherDaily['main']['temp_min']),
        'max': round(weatherDaily['main']['temp_max'])
    }
    weatherPton['current_data'] = result

    weatherData = []
    for i in range(5):
        temp = []
        temp.append(int(weatherPton['list'][i]['main']['temp']))
        timeOfDay = dateTime[weatherPton['list'][i]['dt_txt'][-8:]]
        temp.append(timeOfDay)
        stringCode = weatherPton['list'][i]['weather'][0]['id']
        temp.append(weatherEmoji(int(stringCode), timeOfDay))
        weatherData.append(temp)
    weatherData.append(weatherPton['current_data'])

    return weatherData


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
        "articles": articles
    }


def get_banner():
    data = db.widgets.find_one({'_id': 'data'})
    return data.get("banner", "")


def get_data():
    data = {
        "weather": get_weather(),
        "dhall": get_menus(),
        "prince": get_prince(),
        "timestamp": str(datetime.now()),
        "banner": get_banner()
    }
    return data


db.widgets.replace_one({"_id": "data"}, get_data(), True)

