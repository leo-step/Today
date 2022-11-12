import pymongo
from dotenv import load_dotenv
import os
import requests


load_dotenv()
client = pymongo.MongoClient(os.getenv("DB_CONN"))
db = client.data



# weather = {'_id': 'weather', '9 am' : 68, '12 pm' : 78,  '3 pm' : 38,  '6 pm' : 28 }
lunch = {'_id': 'lunch',
                'Roma' : {'main entree' : 'steak', 'vegetarian entree' : 'beans', 'soup' : 'clam chowder'},
                'NCW' : {'main entree' : 'steak', 'vegetarian entree' : 'beans', 'soup' : 'clam chowder'}

         }


weatherPton = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?lat=40.343899&lon=-74.660049&appid={os.getenv("WEATHER")}&units=imperial').json()

weatherPton['_id'] = 'weather'







# db.widgets.insert_one(weatherPton)
# db.widgets.insert_many([weather, lunch])