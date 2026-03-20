import pymongo

# the password has to be url encoded

uri = "mongodb+srv://paco:your_gay_password@cluster0.zf8nn0j.mongodb.net/?appName=Cluster0"


client = pymongo.MongoClient(uri)

print(client)

db = client["db"]

collection = db["sample_collection"]

collection.insert_one({"what": "your_gay"})
