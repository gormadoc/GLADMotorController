class DebugSerialTarget():
    """description of class"""
    def __init__(self):
        self.motors = ['m1', 'm2']
        self.positions = { 'm1': 7111, 'm2': 7111}
        self.step_resolutions = {'m1': 256, 'm2': 256}
        self.rates = {'m1': 768000, 'm2': 768000}


    def setPosition(self, motor, position):
        self.positions[motor] = position


    def getPosition(self, motor):
        return self.positions[motor]


    def setRate(self, motor, rate):
        self.rates[motor] = rate


    def getRate(self, motor):
        return self.rates[motor]


    def setStepResolution(self, motor, resolution):
        self.step_resolutions[motor] = resolution


    def getStepResolution(self, motor):
        return self.step_resolutions[motor]