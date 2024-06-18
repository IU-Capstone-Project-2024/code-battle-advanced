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

files = os.listdir("./data")
for f in files:
    data = bson.json_util.loads(open(f"./data/{f}", "r").read())
    for table in data:
        if table == "users":
            for i in range(len(data["users"])):
                if "password" in data["users"][i] and type(data["users"][i]["password"]) != bytes:
                    data["users"][i]["password"] = bcrypt.hashpw(data["users"][i]["password"].encode('utf-8'), bcrypt.gensalt(14))
    open(f"./data/{f}", "w").write(bson.json_util.dumps(data, indent=4))
