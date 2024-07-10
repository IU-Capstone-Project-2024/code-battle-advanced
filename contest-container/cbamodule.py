from cbacontest import *

class ContestantData(ContestantDataTemplate):
    def get_test_verdict(self, task: str) -> str:
        return super().get_test_verdict(task)
    
    def get_points(self) -> float:
        return super().get_points()
