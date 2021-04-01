import serial
from PyQt5 import QtWidgets, QtGui, QtCore
from timeit import default_timer
from queue import PriorityQueue
import threading

class DebugSerialTarget(QtWidgets.QWidget):
    """description of class"""
    def __init__(self, log, *args, **kwargs):
        super(DebugSerialTarget, self).__init__(*args, **kwargs)

        # motor values
        self._motors = ['m1', 'm2']
        self._positions = { 'm1': 7111, 'm2': 7111}
        self._step_resolutions = {'m1': 200, 'm2': 200}
        self._rates = {'m1': 768000, 'm2': 768000}
        self._acceleration = {'m1': 0, 'm2': 0}

        # serial port
        self._ser = serial.Serial(baudrate=9600, bytesize=serial.EIGHTBITS, timeout=None)
        self._port = 'COM9'

        # timing
        self._timer = QtCore.QTimer()
        self._tick_time = 100 # 0.1 sec
        self._timer.setInterval(self._tick_time)
        self._timer.timeout.connect(self._tick)
        self._last_tick = default_timer()
        self._delta_t = 0
        self._runtime = {'m1': 0, 'm2': 0}

        # commands: {command, value, time}
        self._current_commands = {'m1': None, 'm2': None}
        self._command_queues = {'m1': PriorityQueue(), 'm2': PriorityQueue()}
        self._waiting = False
        self._read_thread = threading.Thread(target=self.getCommand, daemon=False)

        self.log_file = log


    def start(self):
        try:
            self._ser.port = self._port
            self._ser.open()
        except serial.SerialException:
            self.log("Connection to port " + port + "failed.")

        self._tick_number =  0
        self._timer.start()
        self._last_tick = default_timer()
        self._delta_t = 0
        self._runtime = {'m1': 0, 'm2': 0}
        self._tick()
        self._read_thread.start()
        

    def stop(self):
        self._timer.stop()
        self._ser.close()
        self._read_thread.stop()

    def _tick(self):
        # get delta t
        t = default_timer()
        self._delta_t = t - self._last_tick
        last_tick = self._last_tick
        self._last_tick = t

        # continue running current commands
        m1 = self._current_commands['m1']
        m2 = self._current_commands['m2']
        for m in self._motors:
            c = self._current_commands[m]
            if c:
                complete_flag = False
                self._runtime[m] += self._delta_t

                # check if it would run over
                if self._runtime[m] > c['time']:
                    complete_flag = True

                # perform command
                if c['command'] == 'MA':
                    if complete_flag:
                        self._positions[m] = c['value']
                    else:
                        if self._positions[m] > c['value']:
                            self._positions[m] -= int(self._rates[m]*self._delta_t)
                        else:
                            self._positions[m] += int(self._rates[m]*self._delta_t)
                elif c['command'] == 'SL':
                    if complete_flag:
                        self._positions[m] += int(self._rates[m]*(last-tick - c['time']))
                elif c['command'] == 'VM':
                    self._rates[m] = int(c['value'])
                elif c['command'] == 'PR':
                    if c['parameter'] == 'P':
                        self._write(str(self._positions[m]))
                    if c['parameter'] == 'MS':
                        self._write(str(self._rates[m]))

                # zero out command if complete and ready next command
                if complete_flag:
                    self._current_commands[m] = None
                    #try:
                    #    self._current_commands[m] = self._command_queues[m].get()
                    #except Empty:
                    #    self._current_commands[m] = None
            
        # get new command
        #self.read_thread.start()
        return


    def getCommand(self):
        while(1):
            if self._waiting:
                pass
            self._waiting = True
            msg = self._read()
            self._waiting = False
            if msg:
                words = msg.split(' ') # get rid of newline
                words[-1] = words[-1][:-1]
                motor = self._motors[int(words[0][0])-1]
                command = words[0][1:]
                if command == 'PR':
                    if words[1] == 'P':
                        self._write(str(self._positions[motor]))
                    elif words[1] == 'VM':
                        self._write(str(self._rates[motor]))
                    elif words[1] == 'MS':
                        self._write(str(self._step_resolutions[motor]))
                elif command == 'MA':
                    pos = int(words[1])
                    time_to_take = abs(self._positions[motor] - pos)/self._rates[motor]
                    self._current_commands[motor] = {'command': command, 'value': pos, 'time': time_to_take}
                elif command == 'VM':
                    self._current_commands[motor] = {'command': command, 'value': int(words[1]), 'time': 0}
        return

    def _read(self, command = None):
        response =  self._ser.read_until(size=16).decode('utf-8')
        #print("DebugSerialTarget read: " + response)
        #self.log("DebugSerialTarget read: " + response)
        return response


    def _write(self, msg):
        #print("DebugSerialTarget write: " + msg)
        #self.log("DebugSerialTarget write: " + msg)
        return self._ser.write((msg + '\n').encode('utf-8'))


    def setPosition(self, motor, position):
        self._positions[motor] = position


    def getPosition(self, motor):
        return self._positions[motor]


    def setRate(self, motor, rate):
        self._rates[motor] = rate


    def getRate(self, motor):
        return self._rates[motor]


    def setStepResolution(self, motor, resolution):
        self._step_resolutions[motor] = resolution


    def getStepResolution(self, motor):
        return self._step_resolutions[motor]


    ''' log '''
    def log(self, msg):
        if self.log_file != "":
            with open(self.log_file, 'a') as f:
                print(msg, file=f)
        else:
            print(msg)