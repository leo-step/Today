from flask import Flask, jsonify
from dotenv import load_dotenv
from weather import getWeather
from dining import getDhall
from prince import getArticles

load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({
        "weather": getWeather(),
        "dhall": getDhall(),
        "prince": getArticles()
    })

if __name__ == "__main__":
    app.run()
