from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import pymongo
import os

load_dotenv()

app = Flask(__name__) #, static_folder='frontend/build', static_url_path='/'
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
def index():
    client = pymongo.MongoClient(os.getenv("DB_CONN"))
    db = client[os.getenv("DATABASE")]
    data = db.widgets.find_one({'_id': 'data'})

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
