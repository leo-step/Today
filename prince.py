import pymongo
from dotenv import load_dotenv
import os
import requests


load_dotenv()

def getArticles():
    client = pymongo.MongoClient(os.getenv("DB_CONN"))
    db = client.data

    articles = db.widgets.find_one({'_id': 'prince'})
    

    return articles
