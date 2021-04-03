import serial
from PyQt5 import QtWidgets, QtGui, QtCore
from timeit import default_timer
from queue import PriorityQueue
import threading

class DebugSerialTarget(QtWidgets.QWidget):
    """description of class"""
    def __init__(self, log, *args, **kwargs):
        super(DebugSerialTarget, self).__init__(*args, **kwargs)

        # motor parameters
        self._motors = ['m1', 'm2']
        self._current_position = {'m1': 7111, 'm2': 7111}
        self._current_rate = {'m1': 0, 'm2': 0}
        self._step_resolutions = {'m1': 256, 'm2': 256}
        self._maximum_rates = {'m1': 768000, 'm2': 768000}
        self._accelerations = {'m1': 1000000, 'm2': 1000000}
        self._initial_velocity = {'m1': 1000, 'm2': 1000}

        # values for control
        self._target_position = {'m1': 7111, 'm2': 7111}
        self._last_position = {'m1': 7111, 'm2': 7111}
        self._runtime = {'m1': 0, 'm2': 0}
        self._direction = {'m1': int(0), 'm2': int(0)} # 1 for CW, -1 for CCW, 0 for stationary

        # serial port
        self._ser = serial.Serial(baudrate=9600, bytesize=serial.EIGHTBITS, timeout=None)
        self._port = 'COM9'

        # timing
        self._timer = QtCore.QTimer()
        self._tick_time = 50 # 0.1 sec
        self._timer.setInterval(self._tick_time)
        self._timer.timeout.connect(self._tick)
        self._last_tick = default_timer()
        self._delta_t = 0
        

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
        self._last_tick = t

        # continue running current commands
        for m in self._motors:
            c = self._current_commands[m]
            if c:
                self._runtime[m] += self._delta_t

                # perform command
                if c['command'] == 'MA' or c['command'] == 'MR':
                    self._calculateCurrentPosition(m, self._maximum_rates[m])
                    self._target_position[m] = c['value']
                    # checking for completeness depends on direction
                    if self._direction[m] == 1:
                        # case where we're moving clockwise to a point behind us (like 350 -> 10 through 360)
                        if self._last_position[m] > self._target_position[m]:
                            if self._target_position[m] < self._current_position[m] < self._last_position[m]:
                                # we've overshot
                                self._current_position[m] = self._target_position[m]
                                self.stopMovement(m)
                                self._current_commands[m] = None
                        elif self._current_position[m] > self._target_position[m]:
                            # we've overshot
                            self._current_position[m] = self._target_position[m]
                            self.stopMovement(m)
                            self._current_commands[m] = None 
                    if self._direction[m] == -1:
                        # case where we're moving counter-clockwise to a point ahead of us (like 10 -> 350 through 360)
                        if self._last_position[m] < self._target_position[m]:
                            if self._last_position[m] < self._current_position[m] < self._target_position[m]:
                                # we've overshot
                                self._current_position[m] = self._target_position[m]
                                self.stopMovement(m)
                                self._current_commands[m] = None
                        elif self._current_position[m] < self._target_position[m]:
                            # we've overshot
                            self._current_position[m] = self._target_position[m]
                            self.stopMovement(m)
                            self._current_commands[m] = None
                    # restrict the values to the proper range
                    self._current_position[m] = int(self._current_position[m]  % self.fullRevolution(m))
                elif c['command'] == 'SL':
                    self._calculateCurrentPosition(m, c['value'])
                    # restrict the values to the proper range
                    self._current_position[m] = int(self._current_position[m]  % self.fullRevolution(m))
        return


    def _calculateCurrentPosition(self, motor, maximum_rate):
        m = motor
        pos_rate = int(self._runtime[m]**2 * self._accelerations[m] + self._runtime[m]*self._initial_velocity[m])
        # get current velocity and clamp it if necessary
        if pos_rate > maximum_rate or pos_rate == maximum_rate:
            self._current_rate[m] = self._direction[m] * maximum_rate # clamp rate
            t = (maximum_rate - self._initial_velocity[m]) / self._accelerations[m] # time to reach maximum acceleration: t=(v-vi)/a
            # y = y(t=0)  +/- a*time_spent_accelerating/2 + v*time_at_constant_rate
            self._current_position[m] = self._last_position[m] + int(self._direction[m] * (self._accelerations[m] * t)/2 + self._current_rate[m] * (self._runtime[m] - t))
        else: # straightforward calculation
            self._current_rate[m] = self._direction[m] * pos_rate
            self._current_position[m] = self._last_position[m] + self._direction[m] * int(self._runtime[m]**2 * self._accelerations[m]/2 + self._runtime[m]*self._initial_velocity[m])
        
        return
             
    
    def stopMovement(self, motor):
        self._last_position[motor] = self._current_position[motor]
        self._current_rate[motor] = 0
        self._target_position[motor] = self._current_position[motor]
        self._direction[motor] = 0


    def fullRevolution(self, motor):
        return self._step_resolutions[motor]*200


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

                # respond immediately to print commands
                if command == 'PR':
                    if words[1] == 'P':
                        self._write(str(self._current_position[motor]))
                    elif words[1] == 'VM':
                        self._write(str(self._maximum_rates[motor]))
                    elif words[1] == 'MS':
                        self._write(str(self._step_resolutions[motor]))
                    elif words[1] == 'V':
                        self._write(str(self._current_rate[motor]))
                # move to position
                elif command == 'MA':
                    target = int(words[1])
                    if target == self._current_position[motor]:
                        continue
                    #time_to_take = abs(self._current_position[motor] - target)/self._rates[motor]
                    # two special cases: target and position on opposite sides of wheel but nearest across 360
                    if self._current_position[motor] < self.fullRevolution(motor)/4 and target > self.fullRevolution(motor)*3/4:
                        self._direction[motor] = int(-1)
                    elif self._current_position[motor] > self.fullRevolution(motor)*3/4 and target < self.fullRevolution(motor)/4:
                        self._direction[motor] = int(1)
                    else:
                        self._direction[motor] = int((target - self._current_position[motor])/abs(target - self._current_position[motor]))
                    self._current_commands[motor] = {'command': command, 'value': target}
                # move to relative position
                elif command == 'MR': 
                    delta = int(words[1])
                    target = (self._current_position[motor] + delta) % self.fullRevolution[motor]
                    self._direction[motor] = delta//abs(delta)
                    self._current_commands[motor] = {'command': command, 'value': target}
                elif command == 'SL':
                    rate = int(words[1])
                    if rate == 0:
                        self.stopMovement(motor)
                        self._current_commands[motor] = None
                    else:
                        self._direction[motor] = rate//abs(rate)
                        self._current_commands[motor] = {'command': command, 'value': abs(rate)}
                # set maximum velocity
                elif command == 'VM':
                    self._maximum_rates[motor] = int(words[1])
                # set acceleration
                elif command == 'A':
                    self._accelerations[motor] = int(words[1])
                # set step resolution
                elif command == 'MS':
                    self._step_resolutions[motor] = int(words[1])
        return

    def _read(self, command = None):
        response =  self._ser.read_until(size=16).decode('utf-8')
        return response


    def _write(self, msg):
        return self._ser.write((msg + '\n').encode('utf-8'))


    def setPosition(self, motor, position):
        self._current_position[motor] = position


    def getPosition(self, motor):
        return self._current_position[motor]


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