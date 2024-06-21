import time
import pymongo
import bson
import subprocess
from sys import stderr
import redis
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
        continue
print("{")
for i in db.list_collection_names():
    print(f'"{i}":')
    print(bson.json_util.dumps(list(db[i].find()), indent=4))
    print(",")
print("}")

