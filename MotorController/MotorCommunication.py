import serial


class MotorControlCxn():
    def __init__(self, log, debug=False, *args, **kwargs):
        super(MotorControlCxn, self).__init__(*args, **kwargs)
        self.debug = debug
        if self.debug:
            self.port = None
        else:
            self.port = "COM1"
        
        self.log_file = log
        self.baudrate = 9600
        self.bytesize = serial.EIGHTBITS

        self.ser = serial.Serial(port=None, baudrate = self.baudrate, bytesize=self.bytesize)


    def connect(self):
        try:
            self.ser.port = self.port
        except:
            self.log("Connection to port " + port + "failed.")


    def close(self):
        self.ser.close()


    def isOpen(self):
        if self.debug:
            return True
        else:
            return self.ser.is_open()


    def write(self, command):
        self.log(command)
        if self.debug:
            self.log("Writing to debug port {}".format(self.port))
            return 1
        else:
            return self.ser.write((command + '\n').encode('utf-8'))
        

    def sendCommand(self, command):
        # Determine whether we should wait for a reply or not
        if command[1:3] == "PR":
            # the only reason an exception would be raised is due to timeout
            # no timeout is set by default
            try:
                self.write(command)
                return self.read(command)
            except:
                return 0
        else:
            # the only reason an exception would be raised is due to timeout
            # no timeout is set by default
            try:
                return self.write(command)
            except:
                return 0
        return

         
    def read(self, command = None):
        if self.debug is False:
            response =  self.ser.read_until().decode('utf-8')
            self.log("<\t" + response)
        else:
            response = ""
            if "PR MS" in command:
                response = "256" # default value
                self.log("<\t" + response)
            elif "PR P" in command:
                response = "7111"
                self.log("<\t" + response)
            elif "PR VM" in command:
                response = "768000" # default value
                self.log("<\t" + response)
            return response


    def log(self, msg):
        if self.log_file is not "":
            with open(self.log_file, 'a') as f:
                print(msg, file=f)
        else:
            print(msg)