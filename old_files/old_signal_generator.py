#This file is obsolete, SigGen is now implemented as a flow chart node

from PyQt4 import QtCore, QtGui
import numpy as np
from pyqtgraph.flowchart import Flowchart
import pyqtgraph.metaarray as metaarray

#Doesnt necessarily need to be a QWidget??
class SignalGenerator(QtGui.QWidget):
    #Input parameters are:
    #signal type
    #shared_data: shared data block (unnecessary)
    #flow_chart: Reference to the flow chart
    def __init__(self, signal_type, shared_data, flow_chart, parent=None):
        super(SignalGenerator, self).__init__(parent) #super class constructor
        self.shared_data = shared_data
        self.flow_chart = flow_chart
        self.signal_type = signal_type

        #Create and init update timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1) #SLOW

        #Pointer points to the value that will be updated next
        self.pointer = 0

        #initialize signal generator parameters
        if self.signal_type == 'sin':
            self.amplitude = 1.0
            self.frequency = 5.0
        else:
            self.amplitude = 2.0
            self.frequency = 3.0

    def update(self):
        #TODO fix this ugly if to something more generic.
        if self.signal_type == 'sin':
            # update signal value (sine)
            self.shared_data.signal_value_array[self.pointer] = self.amplitude * np.sin(self.pointer*2*np.pi*self.frequency*0.01)

            # Push the new data set to flow chart
            data = metaarray.MetaArray(self.shared_data.signal_value_array, info=[{'name': 'Time', 'values': np.linspace(0, 1000.0, len(self.shared_data.signal_value_array))}, {}])
            #self.flow_chart.setInput(sigOut=data)
        else: #This is the second generator
            # update signal value (sine)
            self.shared_data.signal_value_array2[self.pointer] = self.amplitude * np.sin(self.pointer*2*np.pi*self.frequency*0.01)

            # Push the new data set to flow chart
            data = metaarray.MetaArray(self.shared_data.signal_value_array2, info=[{'name': 'Time', 'values': np.linspace(0, 1000.0, len(self.shared_data.signal_value_array2))}, {}])
            #self.flow_chart.setInput(sigOut2=data)
        # move pointer
        self.pointer += 1
        
        # Hop to start if we have reached the end
        if self.pointer >= self.shared_data.signal_value_array_size:
            self.pointer = 0
