#!/usr/bin/env python

import time
import pymongo
from bson import ObjectId
import json
import subprocess
from sys import stderr
import redis
import uuid
import hashlib

mongo_uri_docker = "mongodb://adminuser:password123@192.168.49.2:32000/CBA_database?authSource=admin"
mongo_uri_local = "mongodb://localhost"

redis_host = "redis"

def test_task(task_id):
  global db
  
  submission_info = db.submissions.find_one({"_id": ObjectId(task_id)})
  submission_file = "/submissions/" + submission_info['filename']
  task = submission_info["task_name"]
  compiler = submission_info["language"]
  time_limit_ms = "2000"
  verdict = open("verdict.temp", "w")
  code = subprocess.check_call(["bash", "judge.sh", submission_file, task, compiler, time_limit_ms], stdout=verdict)
  verdict.close()
  if code != 0:
    print("Error while testing, check all your files for correctness.", file=stderr)
    return
  verdict = open("verdict.temp", "r").read().strip()
  db.submissions.update_one({"_id": ObjectId(task_id)}, {"$set":{"verdict":verdict}})

if __name__ == "__main__":
  client = pymongo.MongoClient(mongo_uri_docker)
  db = client['CBA_database']
  
  q = redis.StrictRedis(host=redis_host)
  session_id = str(uuid.uuid4())

  print("NEW VERSION4!", flush=True)
  print(f"Worker with sessionID: {session_id}", flush=True)
  print(f"Initial queue state: {q.llen('job2')} not processed, {q.llen('job2:processing')} in progress", flush=True)
  while 1:
    item = q.brpoplpush("job2", "job2:processing", timeout=3)
    if item is not None:
      itemstr = item.decode("utf-8")
      print("Working on " + itemstr, flush=True)
      test_task(itemstr)
      q.lrem("job2:processing", 0, item)
    else:
      print("Waiting for work")
  print("Queue empty, exiting")
