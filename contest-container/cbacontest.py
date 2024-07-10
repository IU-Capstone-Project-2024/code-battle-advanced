from typing import TypeAlias, Any, final

# Test verdict and points (from 0 to 1)
TestVerdict: TypeAlias = tuple[str, float]
TestingResults: TypeAlias = list[TestVerdict]

class Widget():
    parent: str = None
    name: str = "Widget0"
    dirty: bool = False
    
    def __init__(self, name):
        self.name = name
        
    def to_html(self):
        return ""
    
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
    
    def to_html(self):
        return f'<p>{self.text}</p>'

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
      
    def to_html(self):
        return f'<button type="submit" name="btn" value={self.name}>{self.text}</button>'
    
    def __repr__(self):
        return f"TextButtonWidget('{self.name}', '{self.text}')"
        
#class ImageButtonWidget(Widget):
#    text = "Test"
#    
#    def on_press(self):
#        self.text = self.text[::-1]

class WidgetBox(Widget):
    contents: list[str] = []

    def __init__(self, name, contents):
        super().__init__(name)
        self.name = name
        fixedcontents = []
        for i in contents:
            if isinstance(i, Widget):
                fixedcontents.append(i)
            #elif isinstance(i, str):
            #    fixedcontents.append(i)
            else:
                raise ValueError("Box is only supposed to have widgets or their names")
        self.contents = fixedcontents
    
    def to_html(self):
        ret_str = '<div>'
        for i in self.contents:
            ret_str += i.to_html()
        ret_str += '</div>'
        return ret_str
    
    def __repr__(self):
        return f"WidgetBox('{self.name}', {str(self.contents)})"

class HWidgetBox(WidgetBox):
    def to_html(self):
        ret_str = '<div class="hbox">'
        for i in self.contents:
            ret_str += i.to_html()
        ret_str += '</div>'
        return ret_str
    
    def __repr__(self):
        return f"HWidgetBox('{self.name}', {str(self.contents)})"

class VWidgetBox(WidgetBox):
    def to_html(self):
        ret_str = '<div class="vbox">'
        for i in self.contents:
            ret_str += i.to_html()
        ret_str += '</div>'
        return ret_str

    def __repr__(self):
        return f"VWidgetBox('{self.name}', {str(self.contents)})"

class ContestantDataTemplate():
    widgets: list[Widget] = []
    storage: dict[str, Any] = {}
    binds: dict[str, str] = {}
    new_schedules: list[tuple[int, str, dict[str, Any], bool]] = []
    
    time: int = 0
    
    @final
    def __init__(self):
        self.widgets = []
        self.task_results = dict()
        
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
    
    @final
    def render_widgets(self):
        is_root = {i.name:True for i in self.widgets}
        for i in self.widgets:
            if isinstance(i, WidgetBox):
                for j in i.contents:
                    is_root[j.name] = False
        rendered_str = ''
        for i in self.widgets:
            if is_root[i.name]:
                rendered_str += i.to_html()
        return rendered_str
        
    def start_contest(self, caller="Start", **kwargs):
        pass
    
    def default_handler(self, caller, **kwargs):
        if caller == "Judge":
            self.task_results[kwargs['task']] = kwargs['verdict']
        
    def get_test_verdict(self, task: str) -> str:
        if task not in self.task_results:
            return ""
        for i in range(len(self.task_results[task])):
            if self.task_results[task][i][0] != "AC":
                return f"{self.task_results[task][i][0]} {i}"
        return "AC"
    
    def get_points(self) -> float:
        return sum([(self.get_test_verdict(i) == "AC") for i in self.task_results])

