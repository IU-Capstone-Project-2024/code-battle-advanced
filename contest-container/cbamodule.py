from cbacontest import *

class ContestantData(ContestantDataTemplate):
    def get_test_verdict(self, task: str) -> str:
        for i in range(len(self.task_results[task])):
            if self.task_results[task][i][0] != "AC":
                return f"{self.task_results[task][i][0]} {i}"
        return "AC"
    
    def get_points(self) -> float:
        return sum([(self.get_test_verdict(i) == "AC") for i in self.task_results])
