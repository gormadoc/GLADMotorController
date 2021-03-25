from PyQt5 import QtWidgets, QtGui, QtCore
import qdarkstyle

import MotorCommunication
from ReadOnlyDial import ReadOnlyDial


class Motor2Control(QtWidgets.QWidget):
    def __init__(self, connection, log, *args, **kwargs):
        super(Motor2Control, self).__init__(*args, **kwargs)
        
        # Variables of interest
        self.angle = 0
        self.step_resolution = 200 # steps per resolution
        self.rate = 0
        self.constant = False
        self.currently_rotating = False
        self.motorID = 2
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
        #self.timeMonBox = QtWidgets.QLineEdit("")
        #self.timeMonBox.setReadOnly(True)
        #self.timeMonBox.setDisabled(True)
        
        # Monitering layout
        self.monitor = QtWidgets.QGroupBox("Current values")
        self.monitorForm = QtWidgets.QFormLayout()
        self.monitorForm.addRow("Tilt (deg):", self.posMonBox)
        self.monitorForm.addRow("Rate (deg/sec):", self.rotMonBox)
        #self.monitorForm.addRow("Time (sec):", self.timeMonBox)
        self.monitor.setLayout(self.monitorForm)
        self.dialMon = QtWidgets.QWidget()
        self.dialMonLay = QtWidgets.QHBoxLayout()
        self.dialMonLay.addWidget(self.dial)
        self.dialMonLay.addWidget(self.monitor)
        self.dialMon.setLayout(self.dialMonLay)
        
        angleValidator = QtGui.QDoubleValidator(0.0, 90.0, 2)
        rateValidator = QtGui.QDoubleValidator(1.0, 5000000, 2)
        
        # Position controls
        self.posLabel = QtWidgets.QLabel("Tilt (degrees)")
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
        self.timeLabel = QtWidgets.QLabel("Time (sec)")
        self.rotButton = QtWidgets.QPushButton("Set rotation rate")
        self.rotButton.clicked.connect(self.enteredRate)
        rotLayout = QtWidgets.QGridLayout()
        rotLayout.addWidget(self.rotLabel, 0, 0)
        rotLayout.addWidget(self.rotBox, 1, 0)
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


    def setAngle(self, value):
        value = round(value / 360.0 * self.step_resolution * 200)
        round_angle = value * 360.0 / self.step_resolution / 200
        self.connection.sendCommand(str(self.motorID) + "MA " + str(value))
        self.connection.sendCommand(str(self.motorID) + "H")
        self.posMonBox.setText(str(round(round_angle, 3)))
        self.dial.setValue(round_angle)
        self.angle = round_angle
          
        
    def enteredAngle(self):
        angle = self.posBox.text()

        try:
            fangle = float(angle)
        except:
            # throw error
            self.log("No angle entered.")
            return
        if fangle < 0 or fangle > 90:
            # throw error
            self.log("Angle out-of-bounds")
        else:
            self.log("Setting angle: " + str(fangle))
            self.setAngle(fangle)
        return


    def setRate(self, value):
        value = round(value / 360.0 * self.step_resolution * 200)
        round_rate = value * 360.0 / self.step_resolution / 200
        self.connection.sendCommand(str(self.motorID) + "VM " + str(value))
        self.connection.sendCommand(str(self.motorID) + "H")
        self.rotMonBox.setText(str(round(round_rate, 3)))
        self.rate = round_rate


    def enteredRate(self):
        rate = self.rotBox.text()
        try:
            rate = float(rate)
            if rate < 0 or rate > 5000000:
                # throw error
                self.log("Rotation rate out-of-bounds")
            else:    
                self.log("Setting rotation rate: " + str(rate))
                self.setRate(rate)
        except:
            # throw error
            self.log("No rate entered.")
        return


    def getRate(self):
        # Get velocity (in steps)
        stepVel = float(self.connection.sendCommand(str(self.motorID) + "PR VM"))
        angleVel = stepVel * 360.0 / self.step_resolution / 200
        self.rotMonBox.setText(str(round(angleVel, 3)))
        self.rate = angleVel
        return self.rate


    def getAngle(self):
        stepPos = float(self.connection.sendCommand(str(self.motorID) + "PR P"))
        anglePos = stepPos * 360.0 / self.step_resolution / 200
        self.dial.setValue(anglePos)
        self.posMonBox.setText(str(round(anglePos, 3)))
        self.angle = anglePos
        return self.angle


    def hold(self):
        self.connection.sendCommand(str(self.motorID) + "H")


    def log(self, msg):
        msg = "MOTOR2: " + msg
        if self.log_file != "":
            with open(self.log_file, 'a') as f:
                print(msg, file=f)
        else:
            print(msg)