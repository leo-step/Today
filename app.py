from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import pymongo
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__) #, static_folder='frontend/build', static_url_path='/'
CORS(app)

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

@app.route("/")
def index():
    client = pymongo.MongoClient(os.getenv("DB_CONN"))
    db = client.data

    weatherPton = db.widgets.find_one({'_id': 'weather'})

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

    dhallData = db.widgets.find_one({'_id': 'dhall'})

    articles = db.widgets.find_one({'_id': 'prince'})

    result = {
        "weather": weatherData,
        "dhall": dhallData,
        "prince": articles,
        "timestamp": str(datetime.now())
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
