from concurrent import futures
from time import time
from random import uniform
from threading import Thread, Lock
import pymongo
from bson import ObjectId

from bisect import insort

from importlib import import_module

import grpc

import cbacontest

import contest_pb2 as pb2
import contest_pb2_grpc as pb2_grpc

mongo_uri_docker = "mongodb://sUbskr1bet0:1celypuZZl3s@192.168.49.2:32000/CBA_database?authSource=admin"
  
client = pymongo.MongoClient(mongo_uri_docker)
db = client['CBA_database']

import cbacontest
import bson

class Handler(pb2_grpc.ContestServicer):
    def __init__(self):
        super().__init__()
    
    def forward_to_time(self, contest_id, participant_id, time):
        contest = db.contests.find_one({"name":contest_id})
        part_data = db.participants.find_one({"contest_id": contest_id, "participant_id": participant_id})
    
        #config_file = open("cbamodule.py", "wb")
        #config_file.write(contest["config"]['file_data'])
        #config_file.close()
        config = import_module("cbamodule")
        
        tasks = contest["tasks"]
    
        task_results = part_data["task_results"]
    
        profile = config.ContestantData(task_results)
        
        past_events = sorted(contest["global_events"] + part_data["events"])
        
        for i in past_events:
            profile.time = i[0]
            profile.event_handler(i[1], i[2])
            profile.new_schedules = []
        
        new_global_events = sorted(contest["new_global_events"]) + [(999999999999999999, "Terminated", {})]
        new_personal_events = sorted(part_data["new_events"]) + [(999999999999999999, "Terminated", {})]
        y1, y2 = 0, 0
        while new_global_events[y1][0] <= time and new_personal_events[y2][0] <= time:
            if new_global_events[y1][0] <= new_personal_events[y2][0]:
                profile.time = new_global_events[y1][0]
                profile.event_handler(new_global_events[y1][1], new_global_events[y1][2])
                y1 += 1
            else:
                profile.time = new_personal_events[y2][0]
                profile.event_handler(new_personal_events[y2][1], new_personal_events[y2][2])
                y2 += 1
            for i in profile.new_schedules:
                if i[3]:
                    insort(new_global_events, (i[0], i[1], i[2]))
                else:
                    insort(new_personal_events, (i[0], i[1], i[2]))
                profile.new_schedules = []
                    
        widgets = [repr(i) for i in profile.widgets]
                    
        db.participants.update_one({"contest_id": contest_id, "participant_id": participant_id},
                               {"$set": {"new_events": new_personal_events[y2:-1], "widgets": widgets}, 
                                "$push":{"events": {"$each": new_personal_events[:y2]}}})
        db.contests.update_one({"name": contest_id},
                               {"$set": {"new_global_events": new_global_events[y1:-1]}, 
                                "$push":{"global_events": {"$each": new_global_events[:y1]}}})
        
        return profile
    
    
    def handle_event(self, contest_id, participant_id, time, caller, params):
        db.participants.update_one({"contest_id": contest_id, "participant_id": participant_id},
                               {"$push":{"new_events": (time, caller, params)}})
        
        return self.forward_to_time(contest_id, participant_id, time)
      
    
    def check_entry(self, contest, participant):
        if db.participants.find_one({"contest_id": contest, "participant_id": participant}) == None:
            contest_data = db.contests.find_one({"name": contest})
            if contest_data == None:
                raise ValueError(f"{contest} does not exist")
        
            new_entry = {"contest_id": contest, 
                         "participant_id": participant,
                         "final_task_results": {i:"" for i in contest_data["tasks"]},
                         "points": 0,
                         "task_results": {i:[("N/A", 0)] for i in contest_data["tasks"]},
                         "widgets": [],
                         "new_events": [],
                         "events": []}
            db.participants.insert_one(new_entry)
    
    def GoToTime(self, request, context):
        contest = request.contest_id
        participant = request.participant_id
        time = request.time
        
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
        
        db.participants.update_one({"contest_id": contest, "participant_id": participant}, 
                               {"$set":{f"task_results.{task}": verdict}})
        
        profile = self.handle_event(contest, participant, time, "Judge", {})
        
        final_verdict = profile.get_test_verdict(task)
        new_points = profile.get_points()
        
        del profile
        
        db.participants.update_one({"contest_id": contest, "participant_id": participant}, 
                               {"$set":{f"final_task_results.{task}": final_verdict, "points": new_points}})
                               
        db.submissions.update_one({"_id": ObjectId(request.submission_id)}, {"$set":{"final_verdict":final_verdict}})
        
        return pb2.UpdateResponse(changed=False)


    def HandleEvent(self, request, context):
        contest = request.contest_id
        participant = request.participant_id
        time = request.time
        caller = request.caller
        data = request.data
        
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
