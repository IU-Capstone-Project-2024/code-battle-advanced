from cbacontest import *

class ContestantData(ContestantDataTemplate):
    widgets: list[Widget] = []
    storage: dict[str, str] = {}
    task_results: dict[str, TestingResults] = []
    
    def __init__(self, storage = {}, task_results = [], tasks = []):
        self.widgets = []
        self.storage = storage
        self.task_results = task_results
        
        for i in self.widgets:
            i.parent = self
    
    def event_handler(self, caller: str, data: str):
        pass
    
    def get_test_verdict(self, task: str) -> str:
        for i in range(len(self.task_results[task])):
            if self.task_results[task][i][0] != "AC":
                return f"{self.task_results[task][i][0]} {i}"
        return "AC"
    
    def get_points(self) -> float:
        return sum([(self.get_test_verdict(i) == "AC") for i in self.task_results])
