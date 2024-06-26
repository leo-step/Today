import pymongo
from dotenv import load_dotenv
import os

load_dotenv()
client = pymongo.MongoClient(os.getenv("DB_CONN"))
db = client[os.getenv("DATABASE")]

BANNER_TEXT = "🎉 Thank you for downloading the extension! 🎉"

query = {"_id": "data"}
update = { "$set": { "banner": BANNER_TEXT } }

db.widgets.update_one(query, update)
print("updated banner")
