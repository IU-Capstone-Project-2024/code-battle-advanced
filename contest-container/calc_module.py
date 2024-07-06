from cbacontest import *

class ContestantData(ContestantDataTemplate):
    
    def start_contest(self, caller="Start", **kwargs):
        self.num = 0
        self.op = "+"
        self.savenum = 0
        disp = TextWidget("display", "0")
        b1 = TextButtonWidget("b1", "1")
        b2 = TextButtonWidget("b2", "2")
        b3 = TextButtonWidget("b3", "3")
        b4 = TextButtonWidget("b4", "4")
        b5 = TextButtonWidget("b5", "5")
        b6 = TextButtonWidget("b6", "6")
        b7 = TextButtonWidget("b7", "7")
        b8 = TextButtonWidget("b8", "8")
        b9 = TextButtonWidget("b9", "9")
        b0 = TextButtonWidget("b0", "0")
        
        opl = TextButtonWidget("o+", "+")
        omi = TextButtonWidget("o-", "-")
        omul = TextButtonWidget("o*", "*")
        odel = TextButtonWidget("o/", "/")
        
        oeq = TextButtonWidget("o=", "=")
        oclear = TextButtonWidget("oC", "C")
        
        bx1 = HWidgetBox("x1", [b1, b2, b3, opl])
        bx2 = HWidgetBox("x2", [b4, b5, b6, omi])
        bx3 = HWidgetBox("x3", [b7, b8, b9, omul])
        bx4 = HWidgetBox("x4", [oclear, b0, oeq, odel])
        bx5 = VWidgetBox("x5", [disp, bx1, bx2, bx3, bx4])
        self.widgets = [disp, bx5]
    
    def default_handler(self, caller, **kwargs):
        if caller[0] == "b":
            self.num = self.num * 10 + int(caller[1])
        if caller[0] == "o":
            if caller[1] in "+-*/":
                self.savenum = self.num
                self.num = 0
                self.op = caller[1]
            elif caller[1] == "=":
                if self.op == "+":
                    self.num += self.savenum
                elif self.op == "-":
                    self.num -= self.savenum
                elif self.op == "*":
                    self.num *= self.savenum
                elif self.op == "/":
                    self.num //= self.savenum
                self.op = "+"
                self.savenum = 0
            elif caller[1] == "C":
                self.num = 0
                self.op = "+"
                self.savenum = 0
        self.widgets[0].setText(str(self.num))
