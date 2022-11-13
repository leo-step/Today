import pymongo
from dotenv import load_dotenv
import os
import requests


load_dotenv()

def getDhall():
    client = pymongo.MongoClient(os.getenv("DB_CONN"))
    db = client.data

    dhallData = db.widgets.find_one({'_id': 'dhall'})
    

    return dhallData
