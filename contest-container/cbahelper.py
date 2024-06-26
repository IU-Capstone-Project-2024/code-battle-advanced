import cbacontest
import bson

def save_data(contest_id: str, participant_id: str, contestant: cbacontest.ContestantData):
    import pymongo
    mongo_uri_docker = "mongodb://sUbskr1bet0:1celypuZZl3s@192.168.49.2:32000/CBA_database?authSource=admin"
    
    client = pymongo.MongoClient(mongo_uri_docker)
    db = client['CBA_database']
    
    storage = contestant.storage
    widgets = [repr(i) for i in contestant.widgets]
    
    db.participants.update_one({"contest_id": contest_id, "participant_id": participant_id},
                               {"$set": {"storage": storage}, "$set": {"widgets": widgets}})
    
    del contestant
    
    

def load_data(contest_id: str, participant_id: str) -> cbacontest.ContestantData:
    import pymongo
    mongo_uri_docker = "mongodb://sUbskr1bet0:1celypuZZl3s@192.168.49.2:32000/CBA_database?authSource=admin"
    
    client = pymongo.MongoClient(mongo_uri_docker)
    db = client['CBA_database']
    
    contest = db.contests.find_one({"name":contest_id})
    part_data = db.participants.find_one({"contest_id": contest_id, "participant_id": participant_id})
    
    tasks = contest["tasks"]
    
    if part_data == None:
        task_results = {i:[("N/A", 0)] for i in tasks}
        storage = {}
        
    else:
        task_results = part_data["task_results"]
        storage = part_data["storage"]
    
    return cbacontest.ContestantData(storage, task_results, tasks)
