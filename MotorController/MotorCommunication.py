import serial
import DebugSerialTarget
import threading

''' Relevant commands
        xPR: print value of parameter (all in steps)
            P: position
            VM: maximum velocity
            MS: set step resolution
        xMA y: set position to y
        xVM y: set rotation rate
        xH: hold until done


'''

class MotorControlCxn():
    def __init__(self, log, debug=False, *args, **kwargs):
        super(MotorControlCxn, self).__init__(*args, **kwargs)
        self.debug = debug
        if self.debug:
            self.port = 'COM8'
        else:
            self.port = "COM1"
        
        self.log_file = log

        self.baudrate = 9600
        self.bytesize = serial.EIGHTBITS
        self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, bytesize=self.bytesize, timeout=None)

        #self.debug_target = DebugSerialTarget.DebugSerialTarget(log)

        self.read_thread = threading.Thread(target=self.read, daemon=True)


    ''' Serial maintenance functions '''
    def connect(self):
        try:
            self.ser.port = self.port
            self.ser.open()
        except serial.SerialException:
            self.log("Connection to port " + self.port + "failed.")


    def close(self):
        self.ser.close()


    def isOpen(self):
        if self.debug:
            return True
        else:
            return self.ser.is_open()


    ''' Basic read/write functions '''
    def write(self, command):
        self.log(command)
        if False:#self.debug:
            self.log("Writing to debug port {}".format(self.port))
            motor = self.debug_target.motors[int(command[0])-1]
            if command[1:3] == "MA":
                self.debug_target.setPosition(motor, int(command[4:]))
            elif command[1:3] == "VM":
                self.debug_target.setRate(motor, int(command[4:]))
            elif command[1:3] == "MS":
                self.debug_target.setStepResolution(motor, int(command[4:]))
            return 1
        else:
            return self.ser.write((command + '\n').encode('utf-8'))
        

    def sendCommand(self, command):
        # Determine whether we should wait for a reply or not
        if command[1:3] == "PR":
            # the only reason an exception should be raised is due to timeout
            # no timeout is set by default
            try:
                self.write(command)
                #self.log("Writing \"{}\" to port.".format(command))
                #self.debug_target.getCommand()
                return self.read()
            except serial.SerialTimeoutException:
                return 0
        else:
            # the only reason an exception should be raised is due to timeout
            # no timeout is set by default
            try:
                return self.write(command)
            except serial.SerialTimeoutException:
                return 0
        return

         
    def read(self, command = None):
        if self.debug:# is False:
            response =  self.ser.read_until(size=16).decode('utf-8')
            self.log("<\t" + response)
        else:
            response = ""
            if command:
                motor = self.debug_target.motors[int(command[0])-1]
                if "PR MS" in command:
                    response = str(self.debug_target.getStepResolution(motor))
                    self.log("<\t" + response)
                elif "PR P" in command:
                    response = str(self.debug_target.getPosition(motor))
                    self.log("<\t" + response)
                elif "PR VM" in command:
                    response = str(self.debug_target.getRate(motor))
                    self.log("<\t" + response)
        return response


    ''' Abstracted commands '''
    def update(self, motor=3):
        if motor == 1:
            position = self.write("1PR P")
            rate = self.write("1PR MR")
            return {'pos': position, 'rate': rate}
        elif motor == 2:
            position = self.write("2PR P")
            rate = self.write("2PR MR")
            return {'pos': position, 'rate': rate}
        elif motor == 3:
            position1 = self.write("1PR P")
            rate1 = self.write("1PR MR")
            position2 = self.write("2PR P")
            rate2 = self.write("2PR MR")
            return {'m1': {'pos': position1, 'rate': rate1}, 'm2': {'pos': position2, 'rate': rate2}}


    ''' log '''
    def log(self, msg):
        if self.log_file != "":
            with open(self.log_file, 'a') as f:
                print(msg, file=f)
        else:
            print(msg)