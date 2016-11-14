import serial
import serial.tools.list_ports
#import serial.tools as serial_tools

class SerialConnection(QtGui.QWidget):
   
    ADRUINO_LOCATION='/dev/tty.usbmodemfa131'
    TRANSFER_SPEED=14400
    timer
    connection = False
    
    def read_data(self): #Slot that is called when it is time to update
        print "lol"
        
    def __init__:
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.connect(read_data())


    def connectToArduino(self):
        print "Found the following serial ports"
        print serial.tools.list_ports.grep("usbmodemfa1")
        #ser = serial.Serial(ARDUINO_LOCATION, TRANSFER_SPEED,timeout=2)


    def connectionIsAlive(self):
        return False

    def waitAndSetData(self):
        message = ser.readline() #Read line from Arduino
        message = message.rstrip('\n').rstrip('\r')
        #Validate received data. Data is places inside brackets to spot
        #corrupted data. If data was corrupted wait for new data.
        while message[0] != '(' or message[len(message)-1] != ')':
            message = ser.readline()
            message = message.rstrip('\n').rstrip('\r')
      
        #print "received:" + message
        message = message.lstrip('(').rstrip(')')
        values = message.split(',')
        data = []

        for i in values:
            value = i.split(':')
            tuple = (value[0], value[1])
            data.append(tuple)

        controller.setData(data)

        if !connectionIsAlive:
            #TODO

        def closeConnection(self):
            #TODO