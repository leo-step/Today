import pymongo
from dotenv import load_dotenv
import os
import requests


load_dotenv()


dateTime = {
    '00:00:00': '9 pm',
    '03:00:00': '12 am',
    '06:00:00': '3 am',
    '09:00:00': '6 am',
    '12:00:00': '9 am',
    '15:00:00': '12 pm',
    '18:00:00': '3 pm',
    '21:00:00': '6 pm'
}

def weatherEmoji(code):
    if code >= 800:
        if code < 802:
            return '☀️'
        if code == 802:
            return '🌤'
        if code == 803:
            return '⛅️'
        if code == 804:
            return '☁️'
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




def getWeather():
    client = pymongo.MongoClient(os.getenv("DB_CONN"))
    db = client.data

    weatherPton = db.widgets.find_one({'_id': 'weather'})
    weatherData = []

    for i in range(5):
        temp = []
        temp.append(int(weatherPton['list'][i]['main']['temp']))
        temp.append(dateTime[weatherPton['list'][i]['dt_txt'][-8:]])
        stringCode = weatherPton['list'][i]['weather'][0]['id']
        temp.append(weatherEmoji(int(stringCode)))
        weatherData.append(temp)

    return weatherData

myWeather = getWeather()

print(myWeather)