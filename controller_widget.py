from PyQt4 import QtCore, QtGui

import global_data
import serial
import serial.tools.list_ports  # Is this necessary?

class ControllerWidget(QtGui.QWidget):

    #HORIZONTAL_MARGIN = 10.0 #%
    #VERTICAL_MARGIN = 20.0 #%

    CONNECTED_MESSAGE = "Controller connected at "
    NO_CONNECTION_MESSAGE = "Controller not found! Please check that the controller unit is attached to an USB port."

    ARDUINO_ID = 'cu.usbmodemfa131'
    ARDUINO_SNR = '74031303437351100210'
    TRANSFER_SPEED = 28800  # This has to match the one defined in Arduino code!
    serial = serial.Serial()

    def __init__(self, parent=None):
        # Call parent constructor
        super(ControllerWidget, self).__init__(parent)

        #Set layout
        ## Create a grid layout to manage the widgets size and position
        layout = QtGui.QGridLayout()
        self.setLayout(layout)

        # Add connection status widget
        self.status_widget = QtGui.QLabel("Status")
        layout.addWidget(self.status_widget, 0, 0, 1, 8)

        # Add latest message received widget
        self.latest_message_widget = QtGui.QLabel("-")
        layout.addWidget(self.latest_message_widget, 1, 0, 1, 8)

        #Create knob widgets
        self.knob_widgets = []
        self.knob_widget_labels = []
        self.knob_widget_value_labels = []
        for i in range(0, 4):
            self.knob_widgets.append(QtGui.QDial())
            layout.addWidget(self.knob_widgets[i], 2, i, 1, 1)

            self.knob_widget_labels.append(QtGui.QLabel("Pot " + str(i)))
            layout.addWidget(self.knob_widget_labels[i], 3, i, 1, 1)

            self.knob_widget_value_labels.append(QtGui.QLabel("Value: 0.0"))
            layout.addWidget(self.knob_widget_value_labels[i], 4, i, 1, 1)

        # Add latest message received widget
        self.button_status_widget = QtGui.QLabel("-")
        layout.addWidget(self.button_status_widget, 5, 0)

        # Set read rate from Arduino in ms
        self.timer = QtCore.QTimer()
        self.timer.setInterval(10)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.read_data)
        self.timer.start()

    def read_data(self):  # Slot that is called when it is time to read data from Arduino
        if self.serial.isOpen():
            # Check that the connection is still open
            try:
                self.serial.inWaiting()
            except:
                print "Lost connection!"
                self.serial.close()
                return
            #print "Connected. Reading data from " + self.ARDUINO_LOCATION
            self.wait_and_and_set_data()
        else:
            #print "No connection. Trying to make one... "
            self.status_widget.setText(self.NO_CONNECTION_MESSAGE)
            self.status_widget.setStyleSheet("QLabel { color : red; }");
            self.connect_to_arduino()

    # Tries to create a connection with Arduino
    def connect_to_arduino(self):
        ports = serial.tools.list_ports.comports()
        
        # print "Found the following serial ports:"
        for c in ports:
            # print c[2]
            if self.ARDUINO_SNR in c[2]:
                print "Found controller! Making a connection..."
                self.serial = serial.Serial(c[0], self.TRANSFER_SPEED, timeout=2)
                if self.serial.isOpen():
                    print "Connected to " + c[0]
                    self.status_widget.setStyleSheet("QLabel { color : green; }");
                    self.status_widget.setText(self.CONNECTED_MESSAGE + self.ARDUINO_ID)
                else:
                    print "Failed."
        
    def wait_and_and_set_data(self):
        # Request update from arduino
        # self.serial.write("UPDATE_REQUEST")

        message = self.serial.readline()  # Read line from Arduino
        #self.serial.flushInput()  # Discard all data that is left in the buffer
        message = message.rstrip('\n').rstrip('\r')  # Trim the received message

        #print "received:" + message
        self.latest_message_widget.setText(message)

        # Validate received data. Data is places inside brackets to spot
        # corrupted data.
        if len(message) > 0 and message[0] == '(' and message[len(message)-1] == ')':
            self.serial.flushInput()  # Discard all data that is left in the buffer
            # remove brackets from message and split key-value pairs from each other
            message = message.lstrip('(').rstrip(')')
            values = message.split(',')

            # Put values to relevant variables, for example to 'potentiometer_values'
            for i in values:
                value = i.split(':')  # Split key-value to value[0] and value[1]
                if value[0].startswith("POT"):
                    # Get the index from value[0]'s last character
                    index = int(value[0][3])
                    value = int(value[1]) / 10.23  # scale to 10%
                    global_data.potentiometer_values[index] = value

                    # Temp, update knobs on screen
                    self.knob_widgets[index].setValue(value)
                    self.knob_widget_value_labels[index].setText(str(value))
                elif value[0].startswith("BTN"):
                    # Get the index from value[0]'s last character
                    index = int(value[0][3])
                    global_data.button_values[index] = int(value[1])
                elif value[0].startswith("ROT"):
                    # Get the index from value[0]'s last character
                    index = int(value[0][3])
                    global_data.rotatory_values[index] = int(value[1])

            #self.button_status_widget.setText("Button values: " + str(global_data.button_values))  # TEMP
            self.button_status_widget.setText("Rotatory values: " + str(global_data.rotatory_values))
            # print "potentiometer_values: " + str(global_data.potentiometer_values)
