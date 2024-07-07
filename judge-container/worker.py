#!/usr/bin/env python

import time
from datetime import datetime, timedelta
import pymongo
from bson import ObjectId
import json
import subprocess
from sys import stderr
import redis
import uuid
import hashlib
import pathlib
from shutil import rmtree
from zipfile import ZipFile
import os

import grpc

import contest_pb2 as pb2
import contest_pb2_grpc as pb2_grpc

mongo_uri_docker = "mongodb://sUbskr1bet0:1celypuZZl3s@192.168.49.2:32000/CBA_database?authSource=admin"
mongo_uri_local = "mongodb://localhost"

redis_host = "redis"

def get_stub():
    channel = grpc.insecure_channel("192.168.49.2:32002")
    return pb2_grpc.ContestStub(channel)

def test_task(task_id):
    global db
    
    submission_info = db.submissions.find_one({"_id": ObjectId(task_id)})
    
    submission_file = f"/{submission_info['filename']}"
    f = open(submission_file, "wb")
    f.write(submission_info["source"])
    f.close()
    
    task_name = submission_info["task_name"]
    
    task = db.tasks.find_one({"_id": ObjectId(task_name)})
    
    rmtree("/tasks/current")
    os.mkdir("/tasks/current")
    os.mkdir("/tasks/current/tests")
    
    for i in task["input"]:
        open(f'/tasks/current/tests/{i["filename"]}', "wb").write(i["file_data"])
    
    for i in task["checker"]:
        open(f'/tasks/current/{i["filename"]}', "wb").write(i["file_data"])
    
    #zip_handle = ZipFile("/temp.zip")
    #for info in zip_handle.infolist():
    #    zip_handle.extract(info.filename, "tasks/")
    #for info in zip_handle.infolist():
    #    if info.is_dir() and info.filename.count("/") == 1:
    #        if os.path.isdir(f"tasks/{task_name}"):
    #            rmtree(f"tasks/{task_name}")
    #        os.rename("tasks/" + info.filename, "tasks/" + task_name)
    
    compiler = submission_info["language"]
    time_limit_ms = "2000"
    verdict = open("verdict.temp", "w")
    code = subprocess.check_call(["unshare", "-rn", "bash", "judge.sh", submission_file, "current", compiler, time_limit_ms], stdout=verdict)
    verdict.close()
    
    if code != 0:
        print("Error while testing, check all your files for correctness.", file=stderr)
        return
    
    verdict = open("verdict.temp", "r").read().strip()
    verdict = [i.split(" ") for i in verdict.split('\n')]
    
    verdict = [(i[0], int(i[1]), float(i[2]), int(i[3])) for i in verdict]
    
    pathlib.Path.unlink(submission_file)
    db.submissions.update_one({"_id": ObjectId(task_id)}, {"$set":{"verdict":verdict}})
    
    cur_contest_time = datetime.utcnow() - db.contests.find_one({"name":submission_info['contest']})['startTime']
    cur_contest_time = int(cur_contest_time / timedelta(milliseconds=1))
    
    get_stub().UpdateTask(pb2.UpdateMessage(time=cur_contest_time, submission_id=task_id))
                               
    

if __name__ == "__main__":
    client = pymongo.MongoClient(mongo_uri_docker)
    db = client['CBA_database']
    
    q = redis.StrictRedis(host=redis_host)
    session_id = str(uuid.uuid4())

    print("NEW VERSION4!", flush=True)
    print(f"Worker with sessionID: {session_id}", flush=True)
    
    while 1:
        print("Trying to connect to redis...")
        try:
            q.ping()
            break
        except redis.exceptions.ConnectionError:
            continue

    print("Connected!")
    print(f"Initial queue state: {q.llen('job2')} not processed, {q.llen('job2:processing')} in progress", flush=True)
    
    clean_up = q.lock("clean_up")
    
    while 1:
        
        if clean_up.acquire(blocking=False):
            processing = q.lrange("job2:processing", 0, -1)
            for item in processing:
                itemstr, strikes = item.decode("utf-8").split(":")
                if not q.exists(f"job2:claim:{itemstr}"):
                    q.lrem("job2:processing", 0, item)
                    if strikes == "0":
                        db.submissions.update_one({"_id": ObjectId(itemstr)}, {"$set":{"verdict":"JE"}}) 
                    else:
                        q.lpush("job2", f"{itemstr}:{int(strikes) - 1}")
            clean_up.release()
            
        
        item = q.brpoplpush("job2", "job2:processing", timeout=3)
        if item is not None:
            
            itemstr, strikes = item.decode("utf-8").split(":")
            q.setex(f"job2:claim:{itemstr}", 3*60, session_id)
            
            print("Working on " + itemstr, flush=True)
            test_task(itemstr)
            
            q.delete(f"job2:claim:{itemstr}")
            q.lrem("job2:processing", 0, item)
        else:
            print("Waiting for work")
    print("Queue empty, exiting")
