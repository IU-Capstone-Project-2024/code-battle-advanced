from typing import TypeAlias, Any, final

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
        return f"Widget('{self.name}')"
    
class TextWidget(Widget):
    text = "Test Widget"
    
    def __init__(self, name, text):
        super().__init__(name)
        self.text = text
        
    def setText(self, text: str):
        self.text = text
        self.dirty = True
    
    def __repr__(self):
        return f"TextWidget('{self.name}', '{self.text}')"
    
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
        self.parent.event_handler(self.name, "Pressed")
    
    def __repr__(self):
        return f"TextButtonWidget('{self.name}', '{self.text}')"
        
#class ImageButtonWidget(Widget):
#    text = "Test"
#    
#    def on_press(self):
#        self.text = self.text[::-1]

class ContestantDataTemplate():
    widgets: list[Widget] = []
    storage: dict[str, Any] = {}
    binds: dict[str, str] = {}
    new_schedules: list[tuple[int, str, dict[str, Any], bool]] = []
    
    time: int = 0
    
    @final
    def __init__(self, task_results = []):
        self.widgets = []
        self.task_results = task_results
        
        if "*" not in self.binds:
            self.binds["*"] = "default_handler"
        if "Start" not in self.binds:
            self.binds["Start"] = "start_contest"
        
        for i in self.widgets:
            i.parent = self
    
    @final
    def schedule(self, dtime: int, handler, params: dict[str, Any], is_global: bool = False):
        if callable(handler):
            handler = handler.__name__
            
        if dtime <= 0:
            raise ValueError("Time offset must be positive and non-zero")
        
        params["handler"] = handler
        
        self.new_schedules.append((dtime + self.time, "Schedule", params, is_global))
        
    @final
    def bind(self, caller, handler):
        if callable(handler):
            handler = handler.__name__
        
        self.binds[caller] = fhandler
    
    @final
    def event_handler(self, caller: str, event_data: dict[str, Any]):
        if "handler" in event_data:
            foo = getattr(self, event_data.pop("handler"))
        elif caller not in self.binds:
            if "*" in self.binds:
                foo = getattr(self, self.binds["*"])
            else:
               return "Event not binded!"
        else:
            foo = getattr(self, self.binds[caller])
        
        return foo(caller, **event_data)
        
    def start_contest(self, caller="Start", **kwargs):
        pass
    
    def default_handler(self, caller, **kwargs):
        pass
        
    def get_test_verdict(self, task: str) -> str:
        for i in range(len(self.task_results[task])):
            if self.task_results[task][i][0] != "AC":
                return f"{self.task_results[task][i][0]} {i}"
        return "AC"
    
    def get_points(self) -> float:
        return sum([(self.get_test_verdict(i) == "AC") for i in self.task_results])

