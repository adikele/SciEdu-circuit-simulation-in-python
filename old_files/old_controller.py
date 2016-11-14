#This class is not used
class Controller():
    toggleButtons = True

    buttons = [False, False, False, False, False, False, False, False]
    potentiometers = [0, 0, 0, 0]

    def __init__(self):
        
    def setData(self, data):
        if self.getValueOfParameter(data, "Button0") == True: #Button has been pushed
            self.buttons[1] = self.getValueOfParameter(data, "Button1")
            self.buttons[2] = self.getValueOfParameter(data, "Button2")
            self.buttons[3] = self.getValueOfParameter(data, "Button3")
            self.buttons[4] = self.getValueOfParameter(data, "Button4")
            self.buttons[5] = self.getValueOfParameter(data, "Button5")
            self.buttons[6] = self.getValueOfParameter(data, "Button6")
            self.buttons[7] = self.getValueOfParameter(data, "Button7")
        if self.getValueOfParameter(data, "Button0") == True: #Button has been pushed
            if toggleButtons == True:
                self.buttons[0] =! self.buttons[0]
            #TODO launch button pressed event to do something


        self.potentiometers[0] = self.getValueOfParameter(data, "Potentiometer0")
        self.potentiometers[1] = self.getValueOfParameter(data, "Potentiometer1")
        self.potentiometers[2] = self.getValueOfParameter(data, "Potentiometer2")
        self.potentiometers[3] = self.getValueOfParameter(data, "Potentiometer3")

    def getStatusOfButtons(self):
        return self.buttons

    def setToggleButtons(self, toggle):
        self.toggleButtons = toggle

    def toggleButtons(self):
        return self.toggleButtons

    def getStatusOfPotentiometers(self):
        return self.potentiometers

    def getValueOfParameter(self, data, parameterName):
        #search for parameter in data, returns the value of the parameter