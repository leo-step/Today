from flask import Flask, jsonify
from dotenv import load_dotenv
from helper import get_data
from flask_cors import CORS

load_dotenv()

app = Flask(__name__, static_folder='frontend/build', static_url_path='/')
CORS(app)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/api")
def api():
    return jsonify(get_data())

if __name__ == "__main__":
    app.run()
