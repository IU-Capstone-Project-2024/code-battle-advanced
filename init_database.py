import time
import pymongo
from bson import ObjectId
import json
import subprocess
from sys import stderr
import redis
import uuid
import hashlib
import bcrypt

mongo_uri_docker = "mongodb://adminuser:password123@192.168.49.2:32000/CBA_database?authSource=admin"

client = pymongo.MongoClient(mongo_uri_docker)
db = client['CBA_database']

hashed = bcrypt.hashpw("lol".encode('utf-8'), bcrypt.gensalt(14))
db.users.insert_one(
            {'username': "Tedor", 'password': hashed, 'email': "idc_lol", 'admin': True})
