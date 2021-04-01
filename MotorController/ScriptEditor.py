from PyQt5 import QtWidgets, QtGui, QtCore
import qdarkstyle
import MotorCommunication


commands = ['get', 'hold', 'set']
motors = ['m1', 'm2']
parameters = ['position', 'rate']
times = ['for', 'over']


class ScriptEditor(QtWidgets.QWidget):
    def __init__(self, motor1, motor2, log, *args, **kwargs):
        super(ScriptEditor, self).__init__(*args, **kwargs)
        self.motor1 = motor1
        self.motor2 = motor2

        self.editor = QtWidgets.QTextEdit("")
        #self.editor.textChanged.connect(self.textChanged)
        self.editor.setTabStopWidth(8)

        self.output = QtWidgets.QTextEdit("")
        self.output.setReadOnly(True)

        

        self.executeBtn = QtWidgets.QPushButton("Execute")
        self.executeBtn.clicked.connect(self.execute)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.editor)
        layout.addWidget(self.output)
        layout.addWidget(self.executeBtn)
        self.setLayout(layout)


    def execute(self):
        blocks = self.interpretInput()
        for block in blocks:
            out = ""
            if block['motor'] == 'm1':
                if block['command'] == 'get':
                    if block['parameter'] == 'position':
                        out = "Motor 1 position: " + str(self.motor1.getAngle())
                    elif block['parameter'] == 'rate':
                        out = "Motor 1 rate of rotation: " + str(self.motor1.getRate())
                elif block['command'] == 'hold':
                    self.motor1.hold()
                    out = "Motor 1 holding"
                elif block['command'] == 'set':
                    if block['parameter'] == 'position':
                        if block['time'] == '':
                            self.motor1.setAngle(block['value'])
                        else:
                            pass # no implementation yet
                    if block['parameter'] == 'rate':
                        if block['time'] == '':
                            self.motor1.setRate(block['value'])
                        else:
                            pass # no implementation yet
            elif block['motor'] == 'm2':
                if block['command'] == 'get':
                    if block['parameter'] == 'position':
                        out = "Motor 2 position: " + str(self.motor2.getAngle())
                    elif block['parameter'] == 'rate':
                        out = "Motor 2 rate of rotation: " + str(self.motor2.getRate())
                elif block['command'] == 'hold':
                    self.motor2.hold()
                    out = "Motor 2 holding"
                elif block['command'] == 'set':
                    if block['parameter'] == 'position':
                        if block['time'] == '':
                            self.motor1.setAngle(block['value'])
                        else:
                            pass # no implementation yet
                    if block['parameter'] == 'rate':
                        if block['time'] == '':
                            self.motor1.setRate(block['value'])
                        else:
                            pass # no implementation yet

            # user probably wants to know what is happening
            if out:
                self.appendOutput(out)


    def interpretInput(self):
        text = self.editor.toPlainText()
        block = []
        parses = True

        # split new script from old commands
        if text != '':
            self.appendOutput(10 * '-')

        # we want parsed lines and not one large string
        lines = text.split('\n')
        for line in lines:
            line = line.split(' ')

        # Each line is one instruction
        for line in lines:
            # ignore blank lines and comments
            if len(line) < 1 or line[0] == '#':
                continue

            # get each token in the instruction
            words = line.split(' ')

            # get command and ensure it is a command
            try:
                command = words[0]
            except IndexError:
                self.appendOutput("ERROR: No words in line {}.".format(lines.index(line)))
            if command == "Program":
                continue
            elif command not in commands:
                self.appendOutput("ERROR: No recognized command in line {}.".format(lines.index(line)))
                parses = False
                continue

            # get motor
            try:
                motor = words[1]
            except IndexError:
                self.appendOutput("ERROR: No motor designation in line {}.".format(lines.index(line)))
            if motor not in motors:
                self.appendOutput("ERROR: No recognized motor (\'m1\' or \'m2\') in line {}.".format(lines.index(line)))
                parses = False
                continue

            # if command is hold things are easy
            if command == 'hold':
                if motor == 'm1':
                    motor1.hold()
                elif motor == 'm2':
                    motor2.hold()
                continue

            # get parameter (position, rate, ...)
            try:
                parameter = words[2]
            except IndexError:
                self.appendOutput("ERROR: No parameter (position, rate, ...) given in line {}".format(lines.index(line)))
                parses = False
                continue
            if parameter not in parameters:
                self.appendOutput("ERROR: No recognized parameter in line {}.".format(lines.index(line)))
                parses = False
                continue

            # if the command was get we don't need values
            out = ""
            if command == 'get':
                block.append({'motor': motor, 'command': command, 'parameter': parameter})
                continue

            # get value for command
            try:
                value = float(words[3])
            except IndexError:
                self.appendOutput("ERROR: No value given in line {}".format(lines.index(line)))
                parses = False
                continue
            except ValueError:
                self.appendOutput("ERROR: Parameter value must be a number in line {}".format(lines.index(line)))
                parses = False
                continue

            # get timing characteristics (if there are any)
            time = ""
            timespan = 0
            try:
                time = words[4]
            except IndexError:
                # this is okay, we don't need a specified time
                pass

            if time != "":
                try: 
                    timespan = float(words[5])
                except IndexError:
                    self.appendOutput("ERROR: No time span given in line \"{}\"".format(lines.index(line)))
                    parses = False
                    continue
                except ValueError:
                    self.appendOutput("ERROR: Time span must be a number in line \"{}\"".format(lines.index(line)))
                    parses = False
                    continue

            # will change once a scheduler is implemented
            if command == 'set':
                if value < 0:
                    value = value % 360
                if motor == 'm2' and (value < 0 or value > 90):
                    self.appendOutput("ERROR: Motor 2 must be in range 0-90 deg in line {}".format(lines.index(line)))
                    parses = False
                    continue

                block.append({'motor': motor, 'command': command, 'parameter': parameter, 'value': value, 'time': time, 'timespan': timespan})
        if parses:
            return block
        else:
            return []


    def appendOutput(self, string):
        txt = self.output.toPlainText()
        #try:
        txt += string + '\n'
        self.output.setPlainText(txt)
        return

    
    def textChanged(self):
        text = self.editor.toPlainText()
        html_text = ""

        motors = ['m1', 'm2']
        times = ['for', 'over']

        for line in text:
            for word in line:
                if word in motors:
                    pass#word = "<p style=\"color:rgb(0,0,255));\">" + word + "</p>"
                elif word in times:
                    pass
                html_text += word + " "
            html_text += "\n"
        
            print(html_text)
        self.editor.setPlainText(html_text)
        return


    def tick(self):
        # update tick interval
        if self.tick_number == self.update_interval // self.tick_time:
            self.appendOutput("Timer tick")
        self.tick_number %= (self.update_interval // self.tick_time)
        self.tick_number += 1
        return
