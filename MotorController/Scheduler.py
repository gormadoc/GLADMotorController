from PyQt5 import QtWidgets, QtGui, QtCore
import qdarkstyle
import MotorCommunication

from queue import PriorityQueue
from timeit import default_timer

class Scheduler(QtWidgets.QWidget):
    def __init__(self, connection, log, *args, **kwargs):
        super(Scheduler, self).__init__(*args, **kwargs)

        # event timer
        self._timer = QtCore.QTimer()
        self._tick_time = 200 # 0.2 sec
        self._timer.setInterval(self._tick_time)
        self._timer.timeout.connect(self._tick)
        self._tick_number =  0
        self._update_interval = 5000 # 5 sec

        # stop watch
        self._start_time = 0

        # implements the schedule
        self._schedule = PriorityQueue()

        # serial
        self._connection = connection

        self.start()


    def start(self):
        self._timer.start()
        self._start_time = default_timer()
        return


    def end(self):
        self._timer.stop()


    def createSchedule(self, instructions):
        return


    def startSchedule(self):
        self.start()
        return


    def interruptSchedule(self):
        return


    def _tick(self):
        runtime = default_timer() - self._start_time
        if self._schedule.queue and self._schedule.queue[0].value < runtime*1000:
            _execute(self._schedule.pop().command)
        #elif self._tick_number == self._update_interval // self._tick_time:
            # interval to check positions, ignore while we want to send a program command
        #    print("Getting info")
        #    parameters = self._connection.update()
        #    print(parameters)
        self._tick_number %= (self._update_interval // self._tick_time)
        self._tick_number += 1
        return


    def _execute(self, command):
        return


    def abort(self):
        return