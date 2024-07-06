from cbacontest import *

class ContestantData(ContestantDataTemplate):
    
    def start_contest(self, caller="Start", **kwargs):
        self.tindex = 0
        self.btexts = ["Ow", "Ouch", "Stop", "Please", "I dont like this"]
        self.widgets = [TextWidget("display", "Press the button!"),
                        TextButtonWidget("button", "press me!")]
    
    def default_handler(self, caller, **kwargs):
        if caller == "button":
            self.widgets[0].setText(self.btexts[self.tindex % len(self.btexts)])
            self.tindex += 1
        
    def get_test_verdict(self, task: str) -> str:
        for i in range(len(self.task_results[task])):
            if self.task_results[task][i][0] != "AC":
                return f"{self.task_results[task][i][0]} {i}"
        return "AC"
    
    def get_points(self) -> float:
        return sum([(self.get_test_verdict(i) == "AC") for i in self.task_results])
