from PyQt5 import QtWidgets, QtGui, QtCore
import qdarkstyle

import sys, os
import time

from Motor1Control import *
from Motor2Control import *
from ScriptEditor import ScriptEditor
from Scheduler import *
from MotorController import *

from MotorCommunication import *


class MotorControllerWindow(QtWidgets.QMainWindow):
    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            print("escaped")
        return


debug = True

tstart = time.time()

if not os.path.exists("logs/"):
    os.mkdir("logs/")

script_log = r"logs/script_history_" + str(tstart) + ".txt"
if debug is False:
    normal_log = r"logs/log_output_" + str(tstart) + ".txt"
else:
    normal_log = ""

#script_log = logging.getLogger("script")
#normal_log = logging.getLogger("normal")

#script_log.info(str(time.time()))
#normal_log.info(str(time.time()))

app = QtWidgets.QApplication([])
app.setStyle(qdarkstyle.load_stylesheet())
app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))

#ser = MotorControlCxn(script_log, debug=True)

#m1 = Motor1Control(ser, normal_log)
#m2 = Motor2Control(ser, normal_log)
#editor = ScriptEditor(m1, m2, normal_log)
#scheduler = Scheduler(ser, normal_log)

#layout = QtWidgets.QHBoxLayout()
#layout.addWidget(m1)
#layout.addWidget(m2)
#layout.addWidget(editor)
#w = QtWidgets.QWidget()
#w.setLayout(layout)

controller = MotorController(debug, script_log, normal_log)
window = MotorControllerWindow()
window.setCentralWidget(controller)

#window = Motor1Control()
window.show()

app.exec_()

ser.ser.close()