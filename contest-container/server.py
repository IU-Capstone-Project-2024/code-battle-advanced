from concurrent import futures
from time import time
from random import uniform
from threading import Thread, Lock
import pymongo
from bson import ObjectId
import os

from bisect import insort

import importlib

import grpc

import cbacontest
import cbamodule as config

import ast

import contest_pb2 as pb2
import contest_pb2_grpc as pb2_grpc

mongo_uri_docker = f"mongodb://{os.environ['MONGO_INITDB_ROOT_USERNAME']}:{os.environ['MONGO_INITDB_ROOT_PASSWORD']}@192.168.49.2:32000/CBA_database?authSource=admin"
  
client = pymongo.MongoClient(mongo_uri_docker)
db = client['CBA_database']

import cbacontest
import bson

class Handler(pb2_grpc.ContestServicer):
    def __init__(self):
        super().__init__()
    
    def forward_to_time(self, contest_id, participant_id, time):
        contest = db.contests.find_one({"_id": ObjectId(contest_id)})
        part_data = db.participants.find_one({"contest_id": contest_id, "participant_id": participant_id})
    
        config_file = open("cbamodule.py", "wb")
        config_file.write(contest["config"]['file_data'])
        config_file.close()
        importlib.reload(config)
    
        profile = config.ContestantData()
        
        past_events = sorted(part_data["events"])
        
        for i in past_events:
            profile.time = i[0]
            profile.event_handler(i[1], i[2])
            profile.new_schedules = []
            
        new_global_events = []
        new_personal_events = sorted(part_data["new_events"]) + [(999999999999999999, "Terminated", {})]
        y = 0
        while new_personal_events[y][0] <= time:
            profile.time = new_personal_events[y][0]
            profile.event_handler(new_personal_events[y][1], new_personal_events[y][2])
            
            for i in profile.new_schedules:
                if i[3]:
                    insort(new_global_events, (i[0], i[1], i[2]))
                insort(new_personal_events, (i[0], i[1], i[2]))
                profile.new_schedules = []
            y += 1
        
        widgets = profile.render_widgets()
        final_verdicts = {str(task):profile.get_test_verdict(task) for task in contest['tasks']}
        new_points = profile.get_points()
        
        db.participants.update_one({"contest_id": contest_id, "participant_id": participant_id},
                               {"$set": {"new_events": new_personal_events[y:-1], "widgets": widgets,
                                         "final_task_results": final_verdicts, "points": new_points}, 
                                "$push":{"events": {"$each": new_personal_events[:y]}}})
        db.participants.update_many({"contest_id": contest_id, "participant_id": {"$ne": participant_id}},
                               {"$push":{"new_events": {"$each": new_global_events}}})
        db.contests.update_one({"_id": ObjectId(contest_id)},
                               {"$push":{"global_events": {"$each": new_global_events}}})
        
        return profile
    
    
    def handle_event(self, contest_id, participant_id, time, caller, params):
        db.participants.update_one({"contest_id": contest_id, "participant_id": participant_id},
                               {"$push":{"new_events": (time, caller, params)}})
        
        return self.forward_to_time(contest_id, participant_id, time)
      
    
    def check_entry(self, contest, participant):
        if db.participants.find_one({"contest_id": contest, "participant_id": participant}) == None:
            contest_data = db.contests.find_one({"_id": ObjectId(contest)})
            if contest_data == None:
                raise ValueError(f"{contest} does not exist")
        
            new_entry = {"contest_id": contest, 
                         "participant_id": participant,
                         "final_task_results": {str(i):"" for i in contest_data["tasks"]},
                         "points": 0,
                         "widgets": "",
                         "new_events": contest_data["global_events"],
                         "events": []}
            db.participants.insert_one(new_entry)
    
    def GoToTime(self, request, context):
        contest = request.contest_id
        participant = request.participant_id
        time = request.time
        
        self.check_entry(contest, participant)
        
        self.forward_to_time(contest, participant, time)
        
        return pb2.UpdateResponse(changed=False)
    
    def UpdateTask(self, request, context):
        time = request.time
        submission_info = db.submissions.find_one({"_id": ObjectId(request.submission_id)})
        
        contest = submission_info["contest"]
        participant = submission_info["sender"]
        task = submission_info["task_name"]
        verdict = submission_info["verdict"]
    
        self.check_entry(contest, participant)
        
        profile = self.handle_event(contest, participant, time, "Judge", {"task":submission_info['task_name'],
                                                                          "source":submission_info['source'],
                                                                          "n_try":submission_info['n_try'],
                                                                          'language':submission_info['language'],
                                                                          'verdict':submission_info['verdict']})
                                                                          
        db.submissions.update_one({"_id": ObjectId(request.submission_id)}, {"$set":{"final_verdict":profile.get_test_verdict(task)}})
        
        return pb2.UpdateResponse(changed=False)


    def HandleEvent(self, request, context):
        contest = request.contest_id
        participant = request.participant_id
        time = request.time
        caller = request.caller
        data = ast.literal_eval(request.data)
        
        self.check_entry(contest, participant)
        
        self.handle_event(contest, participant, time, caller, data)
                
        return pb2.UpdateResponse(changed=False)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    pb2_grpc.add_ContestServicer_to_server(Handler(), server)
    server.add_insecure_port("[::]:5000")
    try:
        server.start()
        while True:
            server.wait_for_termination()
    except grpc.RpcError as e:
        print(f"Unexpected Error: {e}")
    except KeyboardInterrupt:
        server.stop(grace=10)
        print("Shutting Down...")

if __name__ == "__main__":
    client = pymongo.MongoClient(mongo_uri_docker)
    db = client['CBA_database']
    
    serve()
