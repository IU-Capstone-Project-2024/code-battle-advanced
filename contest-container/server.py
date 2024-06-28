from concurrent import futures
from time import time
from random import uniform
from threading import Thread, Lock
import pymongo
from bson import ObjectId

import grpc

import cbahelper, cbacontest

import contest_pb2 as pb2
import contest_pb2_grpc as pb2_grpc

mongo_uri_docker = "mongodb://sUbskr1bet0:1celypuZZl3s@192.168.49.2:32000/CBA_database?authSource=admin"

class Handler(pb2_grpc.ContestServicer):
    def __init__(self):
        super().__init__()
        
    
    def check_entry(self, contest, participant):
        if db.participants.find_one({"contest_id": contest, "participant_id": participant}) == None:
            contest_data = db.contests.find_one({"name": contest})
            if contest_data == None:
                raise ValueError(f"{contest} does not exist")
        
            profile = cbahelper.load_data(contest, participant)
        
            new_entry = {"contest_id": contest, 
                         "participant_id": participant,
                         "final_task_results": {i:"" for i in contest_data["tasks"]},
                         "points": 0,
                         "task_results": {i:[("N/A", 0)] for i in contest_data["tasks"]}, 
                         "storage": {},
                         "widgets": []}
            db.participants.insert_one(new_entry)
        
            cbahelper.save_data(contest, participant, profile)
    
    def UpdateTask(self, request, context):
        submission_info = db.submissions.find_one({"_id": ObjectId(request.submission_id)})
        
        contest = submission_info["contest"]
        participant = submission_info["sender"]
        task = submission_info["task_name"]
        verdict = submission_info["verdict"]
    
        self.check_entry(contest, participant)
        
        db.participants.update_one({"contest_id": contest, "participant_id": participant}, 
                               {"$set":{f"task_results.{task}": verdict}})
    
        profile = cbahelper.load_data(contest, participant)
        final_verdict = profile.get_test_verdict(task)
        new_points = profile.get_points()
        cbahelper.save_data(contest, participant, profile)
    
        db.participants.update_one({"contest_id": contest, "participant_id": participant}, 
                               {"$set":{f"final_task_results.{task}": final_verdict}})
        db.participants.update_one({"contest_id": contest, "participant_id": participant}, 
                               {"$set":{"points": new_points}})
                               
        db.submissions.update_one({"_id": ObjectId(request.submission_id)}, {"$set":{"final_verdict":final_verdict}})
        
        return pb2.UpdateResponse(changed=False)


    def HandleEvent(self, request, context):
        contest = request.contest_id
        participant = request.participant_id
        caller = request.caller
        data = request.data
        
        self.check_entry(contest, participant)
        
        profile = cbahelper.load_data(contest, participant)
        profile.event_handler(caller, data)
        cbahelper.save_data(contest, participant, profile)
        
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
