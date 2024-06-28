from typing import TypeAlias, Any

# Test verdict and points (from 0 to 1)
TestVerdict: TypeAlias = tuple[str, float]
TestingResults: TypeAlias = list[TestVerdict]

class Widget():
    parent = None
    name: str = "Widget0"
    dirty: bool = False
    
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return f"Widget({self.name})"
    
class TextWidget(Widget):
    text = "Test Widget"
    
    def __init__(self, name, text):
        super().__init__(name)
        self.text = text
        
    def setText(self, text: str):
        self.text = text
        self.dirty = True
    
    def __repr__(self):
        return f"TextWidget({self.name}, {self.text})"
    
#class ImageWidget(Widget):
#    image = "test ignore"
#    
#    def __repr__(self):
#        return f"ImageWidget({self.image})"
    
class TextButtonWidget(Widget):
    text = "Test"
    
    def __init__(self, name, text):
        super().__init__(name)
        self.text = text
    
    def setText(self, text: str):
        self.text = text
        self.dirty = True
    
    def on_press(self):
        self.parent.button_pressed(self.name)
    
    def __repr__(self):
        return f"TextButtonWidget({self.name}, {self.text})"
        
#class ImageButtonWidget(Widget):
#    text = "Test"
#    
#    def on_press(self):
#        self.text = self.text[::-1]

class ContestantDataTemplate():
    widgets: list[Widget] = []
    storage: dict[str, str] = {}
    task_results: dict[str, TestingResults] = []
    
    def __init__(self, storage = {}, task_results = [], tasks = []):
        self.widgets = []
        self.storage = storage
        self.task_results = task_results
        
        for i in self.widgets:
            i.parent = self
    
    def event_handler(self, caller: str, event_data: str):
        pass
    
    def get_test_verdict(self, task: str) -> str:
        for i in range(len(self.task_results[task])):
            if self.task_results[task][i][0] != "AC":
                return f"{self.task_results[task][i][0]} {i}"
        return "AC"
    
    def get_points(self) -> float:
        return sum([(self.get_test_verdict(i) == "AC") for i in self.task_results])

