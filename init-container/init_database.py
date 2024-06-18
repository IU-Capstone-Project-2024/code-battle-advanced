import time
import pymongo
import bson
import subprocess
from sys import stderr
import uuid
import hashlib
import bcrypt
import os
import base64

mongo_uri_docker = "mongodb://sUbskr1bet0:1celypuZZl3s@192.168.49.2:32000/CBA_database?authSource=admin"

client = pymongo.MongoClient(mongo_uri_docker)
db = client['CBA_database']

while 1:
    try:
        client.server_info()
        break
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Database unavailable, retrying...")
        continue

print("Connected to database")

files = os.listdir("./data")
for f in files:
    data = bson.json_util.loads(open(f"./data/{f}", "r").read())
    for table in data:
        if table == "users":
            for i in data["users"]:
                if ("username" not in i or
                   "password" not in i or
                   "email" not in i or
                   "admin" not in i):
                   print(f"Not correct format for entry {i}")
            
                if type(i["password"]) != bytes:
                    i["password"] = bcrypt.hashpw(i["password"].encode('utf-8'), bcrypt.gensalt(14))
                
                db.users.insert_one(i)

print("Success!")
