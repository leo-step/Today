from flask import Flask, request
import pymongo
from dotenv import load_dotenv
import os
from weather import getWeather
load_dotenv()
client = pymongo.MongoClient(os.getenv("DB_CONN"))
db = client.data

app = Flask(__name__)

@app.route("/")
def index():
    return getWeather()


if __name__ == "__main__":
    app.run()