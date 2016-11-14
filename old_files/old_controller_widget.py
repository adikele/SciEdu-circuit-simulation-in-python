from PyQt4 import QtCore, QtGui
import serial
import serial.tools.list_ports

class ControllerWidget(QtGui.QWidget):

    HORIZONTAL_MARGIN = 10.0 #%
    VERTICAL_MARGIN = 20.0 #%
    timer =  QtCore.QTimer()
    
    ARDUINO_LOCATION='/dev/tty.usbmodemfa131'
    TRANSFER_SPEED=14400
    serial = serial.Serial()
    
    def __init__(self, parent=None):
        self.timer.setInterval(800)
        
        super(ControllerWidget, self).__init__(parent)
        
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"),self.read_data)
        self.timer.start()
        
    def read_data(self): #Slot that is called when it is time to update
        if self.serial.isOpen():
            print "Connected. Reading data from " + ARDUINO_LOCATION
            #self.waitAndSetData()
        else:
            #print "No connection. Trying to make one"
            self.connect_to_arduino()
    
    def connect_to_arduino(self):
        ports = serial.tools.list_ports.comports()
        
        #print "Found the following serial ports:"
        for c in serial.tools.list_ports.comports():
            #print c[0]
            if (c[0] == self.ARDUINO_LOCATION):
                print "Found controller! Making a connection..."
                #self.serial = serial.Serial(self.ARDUINO_LOCATION, self.TRANSFER_SPEED,timeout=2)
                if self.serial.isOpen():
                    print "Connected."
                else:
                    print "Failed."

        
    def waitAndSetData(self):
        data
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

        #currentExercise.handleData(data)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        #start
        qp.begin(self)
        #Draw grey box
        qp.setPen(QtGui.QColor(20, 20, 20))
        controller_rect = QtCore.QRect((self.HORIZONTAL_MARGIN/100.0)*self.width(), (self.VERTICAL_MARGIN/100.0)*self.height(), ((100.0-2.0*self.HORIZONTAL_MARGIN)/100.0)*self.width(),((100.0-2.0*self.VERTICAL_MARGIN)/100.0)*self.height())
        qp.fillRect(controller_rect, QtGui.QColor(160, 160, 160))
        qp.drawRect(controller_rect)
        #Draw status of controller
        qp.setFont(QtGui.QFont('Decorative', 12))

        if self.serial.isOpen():
            qp.setPen(QtGui.QColor(0, 255, 0))
            qp.drawText(controller_rect.x(), controller_rect.y(), "Controller connected.")
            qp.drawEllipse (controller_rect.x(), controller_rect.y(), 0.03*self.width(), 0.03*self.width())
        else:
            qp.setPen(QtGui.QColor(250, 30, 30))
            qp.drawText(controller_rect.x(), controller_rect.y(), "Controller not connected!")
            qp.drawEllipse (controller_rect.x(), controller_rect.y(), 0.03*self.width(), 0.03*self.width())
        #Draw buttons
        
        #finish
        qp.end()
