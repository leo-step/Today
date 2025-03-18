from pymongo import MongoClient

client = MongoClient("mongodb+srv://shreyas:3dchcV4llemeQ2CS@cluster0.jx6ja.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

print(client.list_database_names())

db = client['todaycrawl']
col = db['customers']
mydict = { "name": "John", "address": "Highway 37" }
x = col.insert_one(mydict)
print(db)
print(x)