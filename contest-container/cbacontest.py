from typing import TypeAlias

# Test verdict and points (from 0 to 1)
TestVerdict: TypeAlias = tuple[str, float]

class TestingResults():
    verdict: TestVerdict = ("N/A", 0)
    test_results: list[TestVerdict] = []

class ContestantData():
    task_results: list[TestingResults] = []
    
    def get_points(self) -> float:
        return sum([sum([j[1] for j in i.test_results]) / len(i.test_results) for i in self.task_results])
        
    def get_headers(self) -> list[str]:
        return ["Test header"]

    
