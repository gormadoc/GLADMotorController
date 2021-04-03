from PyQt5 import QtWidgets, QtGui, QtCore
import qdarkstyle
import MotorCommunication

from ReadOnlyDial import ReadOnlyDial


class Motor1Control(QtWidgets.QWidget):
    def __init__(self, connection, log, *args, **kwargs):
        super(Motor1Control, self).__init__(*args, **kwargs)
        
        # Variables of interest
        self.angle = 0
        self.step_resolution = 200 # steps per resolution
        self.rate = 0
        self.constant = False
        self.currently_rotating = False
        self.motorID = 1
        self.connection = connection
        self.log_file = log
        
        # Angle Dial
        self.dial = ReadOnlyDial()
        self.dial.setMinimum(0)
        self.dial.setMaximum(360)
        self.dial.setWrapping(True)
        
        # Value reading
        self.posMonBox = QtWidgets.QLineEdit("")
        self.posMonBox.setReadOnly(True)
        self.posMonBox.setDisabled(True)
        self.rotMonBox = QtWidgets.QLineEdit("")
        self.rotMonBox.setReadOnly(True)
        self.rotMonBox.setDisabled(True)
        self.timeMonBox = QtWidgets.QLineEdit("")
        self.timeMonBox.setReadOnly(True)
        self.timeMonBox.setDisabled(True)
        
        # Monitering layout
        self.monitor = QtWidgets.QGroupBox("Current values")
        self.monitorForm = QtWidgets.QFormLayout()
        self.monitorForm.addRow("Rotation (deg):", self.posMonBox)
        self.monitorForm.addRow("Rate (deg/sec):", self.rotMonBox)
        self.monitorForm.addRow("Time (sec):", self.timeMonBox)
        self.monitor.setLayout(self.monitorForm)
        self.dialMon = QtWidgets.QWidget()
        self.dialMonLay = QtWidgets.QHBoxLayout()
        self.dialMonLay.addWidget(self.dial)
        self.dialMonLay.addWidget(self.monitor)
        self.dialMon.setLayout(self.dialMonLay)
        
        angleValidator = QtGui.QDoubleValidator(-360.0, 360.0, 2)
        rateValidator = QtGui.QDoubleValidator(1.0, 5000000, 2)
        
        # Position controls
        self.posLabel = QtWidgets.QLabel("Rotation (degrees)")
        self.posBox = QtWidgets.QLineEdit("")
        self.posBox.setPlaceholderText("Enter tilt")
        self.posBox.setValidator(angleValidator)
        self.posBox.returnPressed.connect(self.enteredAngle)
        self.posButton = QtWidgets.QPushButton("Set angle")
        self.posButton.clicked.connect(self.enteredAngle)
        
        # Rotation rate controls
        self.rotLabel = QtWidgets.QLabel("Rotation rate (degrees/sec)")
        self.rotBox = QtWidgets.QLineEdit("")
        self.rotBox.setPlaceholderText("Enter rotation rate")
        self.rotBox.setValidator(rateValidator)
        self.rotBox.returnPressed.connect(self.enteredRate)
        self.rotCheckLabel = QtWidgets.QLabel("Constant rotation (y/n)")
        self.rotCheck = QtWidgets.QCheckBox()
        self.rotCheck.clicked.connect(self.constantRotation)
        self.timeLabel = QtWidgets.QLabel("Time (sec)")
        self.rotButton = QtWidgets.QPushButton("Set rotation rate")
        self.rotButton.clicked.connect(self.enteredRate)
        rotLayout = QtWidgets.QGridLayout()
        rotLayout.addWidget(self.rotLabel, 0, 0)
        rotLayout.addWidget(self.rotCheckLabel, 0, 1)
        rotLayout.addWidget(self.rotBox, 1, 0)
        rotLayout.addWidget(self.rotCheck, 1, 1)
        self.rotStuff = QtWidgets.QWidget()
        self.rotStuff.setLayout(rotLayout)
        
        # Create layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.dialMon)
        layout.addWidget(self.posLabel)
        layout.addWidget(self.posBox)
        layout.addWidget(self.posButton)
        layout.addWidget(self.rotStuff)
        layout.addWidget(self.rotButton)
        self.setLayout(layout)

        self.initMotor()
        

    def initMotor(self):
        if(self.connection.isOpen()):
            # Most important to get step resolution first
            self.step_resolution = float(self.connection.sendCommand(str(self.motorID) + "PR MS"))

            # Get position (in steps)
            stepPos = float(self.connection.sendCommand(str(self.motorID) + "PR P"))
            anglePos = stepPos * 360.0 / self.step_resolution / 200
            self.dial.setValue(anglePos)
            self.posMonBox.setText(str(round(anglePos, 3)))
            self.angle = anglePos

            # Get velocity (in steps)
            stepVel = float(self.connection.sendCommand(str(self.motorID) + "PR VM"))
            angleVel = stepVel * 360.0 / self.step_resolution / 200
            self.rotMonBox.setText(str(round(angleVel, 3)))
            self.rate = angleVel
        return


    def setAngle(self, value):
        value = round(value / 360.0 * self.step_resolution * 200)
        round_angle = value * 360.0 / self.step_resolution / 200
        self.connection.sendCommand(str(self.motorID) + "MA " + str(value))
        self.connection.sendCommand(str(self.motorID) + "H")

            
    def enteredAngle(self):
        angle = self.posBox.text()
        try:
            fangle = float(angle)
        except:
            # throw error
            self.log("No angle entered.")
            return
        if fangle < -360 or fangle > 360:
            # throw error
            self.log("Angle " + angle + " out-of-bounds")
        else:
            self.log("Setting angle: " + angle)
            self.setAngle(fangle)
        return
        

    def getAngle(self):
        stepPos = float(self.connection.sendCommand(str(self.motorID) + "PR P"))
        anglePos = stepPos * 360.0 / self.step_resolution / 200
        self.dial.setValue(anglePos)
        self.posMonBox.setText(str(round(anglePos, 3)))
        self.angle = anglePos
        return self.angle


    def rotateContinuously(self, value):
        if self.currently_rotating is False:
            value = round(value / 360.0 * self.step_resolution * 200)
            round_rate = value * 360.0 / self.step_resolution / 200 
            self.connection.sendCommand(str(self.motorID) + "SL " + str(value))
            self.rotMonBox.setText(str(round(round_rate, 3)))
            self.rotButton.setText("Stop constant rotation")
            self.currently_rotating = True
            self.log("Rotating continuously at " + str(round_rate) + " deg/sec.")
            self.rotCheck.setDisabled(True)
        else:
            self.connection.sendCommand(str(self.motorID) + "SL 0")
            self.rotMonBox.setText("")
            self.rotButton.setText("Start constant rotation")
            self.currently_rotating = False
            self.log("Stopped rotating.")
            self.rotCheck.setDisabled(False)


    def stopImmediately(self):
        self.connection.sendCommand(str(self.motorID) + "SL 0")


    def setRate(self, value):
        value = round(value / 360.0 * self.step_resolution * 200)
        round_rate = value * 360.0 / self.step_resolution / 200
        self.connection.sendCommand(str(self.motorID) + "VM " + str(value))


    def enteredRate(self):
        rate = self.rotBox.text()
        try:
            rate = float(rate)
            if rate < -5000000 or rate > 5000000:
                # throw error
                self.log("Rotation rate " + rate + " out-of-bounds")
            elif self.constant is False:    
                self.log("Setting rotation rate: " + str(rate))
                self.setRate(rate)
            else:
                # perform a constant rotation until stopped (for a time?)
                self.rotateContinuously(rate)
        except TypeError:
            # throw error
            self.log("No rate entered.")
        return

    
    def getRate(self):
        # Get velocity (in steps)
        stepVel = float(self.connection.sendCommand(str(self.motorID) + "PR V"))
        angleVel = stepVel * 360.0 / self.step_resolution / 200
        self.rotMonBox.setText(str(round(angleVel, 3)))
        self.rate = angleVel
        return self.rate


    def constantRotation(self):
        self.constant = not self.constant
        
        if self.constant is True:
            rateValidator = QtGui.QDoubleValidator(-5000000, 5000000, 2)
            self.posBox.setText("")
            self.posBox.setDisabled(True)
            self.posButton.setDisabled(True)
            self.rotButton.setText("Start constant rotation")
            self.rotMonBox.setText("")
        else:
            rateValidator = QtGui.QDoubleValidator(1.0, 5000000, 2)
            self.posBox.setDisabled(False)
            self.posButton.setDisabled(False)
            self.rotButton.setText("Set rotation rate")
            self.rotMonBox.setText(str(self.rate))
        self.rotBox.setValidator(rateValidator)
        return


    def goToPositionOverTime(self, position, time):
        self.setRate((position - self.angle) / time)
        self.setAngle(position)


    def hold(self):
        self.connection.sendCommand(str(self.motorID) + "H")


    def update(self):
        self.getAngle()
        self.getRate()


    def log(self, msg):
        msg = "MOTOR1: " + msg
        if self.log_file != "":
            with open(self.log_file, 'a') as f:
                print(msg, file=f)
        else:
            print(msg)
