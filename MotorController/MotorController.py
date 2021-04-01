from PyQt5 import QtWidgets, QtGui, QtCore
import qdarkstyle

import sys, os
import time
from timeit import default_timer

import DebugSerialTarget
from Motor1Control import *
from Motor2Control import *
from ScriptEditor import ScriptEditor
from Scheduler import *

from MotorCommunication import *

class MotorController(QtWidgets.QWidget):
    def __init__(self, debug, script_log, normal_log, *args, **kwargs):
        super(MotorController, self).__init__(*args, **kwargs)

        self.debug = debug

        # all of the components we need for the controller
        self._dummy_controller = DebugSerialTarget.DebugSerialTarget(script_log)
        self.ser = MotorControlCxn(script_log, debug=debug)
        self._dummy_controller.start()

        self.m1 = Motor1Control(self.ser, normal_log)
        self.m2 = Motor2Control(self.ser, normal_log)
        self.editor = ScriptEditor(self.m1, self.m2, normal_log)
        self.scheduler = Scheduler(self.ser, normal_log)

        # layout
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.m1)
        self.layout.addWidget(self.m2)
        self.layout.addWidget(self.editor)
        self.setLayout(self.layout)

        # this clock will drive our timed commands
        self._clock = QtCore.QTimer()
        self._tick_time = 100 # 0.1 sec
        self._clock.setInterval(self._tick_time)
        self._clock.timeout.connect(self._tick)
        self._tick_number =  0
        self._update_interval = 500 # 200 msec
        self._last_tick = default_timer()
        self._delta_t = 0

        self._clock.start()
        

    def _tick(self):
        # get delta t
        t = default_timer()
        self._delta_t = t - self._last_tick
        last_tick = self._last_tick
        self._last_tick = t

        if self._tick_number == self._update_interval // self._tick_time:
            # interval to check positions, ignore while we want to send a program command
            self.m1.update()
            self.m2.update()
        self._tick_number %= (self._update_interval // self._tick_time)
        self._tick_number += 1