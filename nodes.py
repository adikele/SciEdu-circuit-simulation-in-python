"""
13.12.2016 PRBS Node in polynomial logic added"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyqtgraph.flowchart import Node
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.flowchart.library.common import CtrlNode
import pyqtgraph.metaarray as metaarray
import scipy.signal
import global_data
import numpy as np
import PRBSnodeFunctions as prbs

from oscilloscope import Oscilloscope
from pyqtgraph.dockarea import *

class BinDataSourceNode(CtrlNode):
    """Node that outputs binary selcted data sequence over whole output array"""
    """ This node, CharToBin and SigGen give error message when inserted and run Scipy with IDLE: Warning (from warnings module):
    File "C:\Python27\lib\site-packages\pyqtgraph\metaarray\MetaArray.py", line 346
    c = getattr(a, op)(b)
    FutureWarning: comparison to `None` will result in an elementwise object comparison in the future."""
    
    nodeName = 'BinDataSource'

    uiTemplate = [
        ('Data Type','combo', {'values': ['000...', '111...', '1010...'], 'index': 0}),
    ]

    def __init__(self, name):
        terminals = {
            'Out': dict(io='out'),
        }
        CtrlNode.__init__(self, name, terminals=terminals)

        self.data_size = global_data.BUFFER_SIZE #10000
        self.batch_size = self.data_size #/ 10 # Update the whole signal buffer at once
        self.block_count = self.data_size / self.batch_size # =1
        self.data = [0] * self.data_size  # Signal data buffer

        # Create and init update timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateSignal)
        self.timer.start(global_data.UPDATE_INTERVAL)

        # Pointer points to the value that will be updated next
        #self.pointer = 0

    def updateSignal(self): # this function is called in regular periods of UPDATE_INTERVAL
        data_type = self.ctrls['Data Type'].currentText()

        # Update the signal buffer array depending on the data type
        for i in range(self.data_size/self.block_count): # i = 0...9999
            #index = self.pointer * self.data_size/self.block_count + i # index = 0*10000/1+0, 1*10000/1+1, 2*10000+2  ???
            #index = i
            if data_type == '000...':
                self.data[i] = 0
            elif data_type == '111...':
                self.data[i] = 1
            elif data_type == '1010...':
                self.data[i] = (i % 2 == 0)# Place 0 binary 1 and 10000 binary 0. Why not 0...9999?
        # move pointer
        #self.pointer += 1
        
        # Hop to start if we have reached the end
        #if self.pointer >= self.block_count: # i >= 1 ???
        #if self.pointer >= self.data_size: #This does not work
        #    self.pointer = 0
        
        #Force the update of output values
        self.update(signal=True)

    def process(self, display=True):
        #Create meta array from updated data
        out_data = metaarray.MetaArray(self.data, info=[{'name': 'Time', 'values': np.linspace(0, len(self.data), len(self.data))}, {}])
        #Set outputs
        return {'Out': out_data}

class PRBSNode(CtrlNode):
    '''Node that generates PRBS according to polynomial logic. Currently a polynomial and seed are fed to this node.
    TODO: Add more polynomials so as to generate varying PRBS; provide option to user in the interface to choose a polynomial.'''
    nodeName = 'PRBSNode'
    uiTemplate = [
        ('Data Type','combo', {'values': ['4-bit LFSR', '111...', '1010...'], 'index': 0}),
    ]

    def __init__(self, name):
        terminals = {
            'Out': dict(io='out'),
        }
        CtrlNode.__init__(self, name, terminals=terminals)

        self.data_size = global_data.BUFFER_SIZE #10000
        self.batch_size = self.data_size #/ 10 # Update the whole signal buffer at once
        self.block_count = self.data_size / self.batch_size # =1
        self.data = [0] * self.data_size  # Signal data buffer

        # Create and init update timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateSignal)
        self.timer.start(global_data.UPDATE_INTERVAL)


    def updateSignal(self): # this function is called in regular periods of UPDATE_INTERVAL
        data_type = self.ctrls['Data Type'].currentText()

        # Update the signal buffer array depending on the data type
        for i in range(self.data_size/self.block_count): # i = 0...9999            
            if data_type == '4-bit LFSR':
                #adding code
                list1 = prbs.polyParser ("1x4 + 1x3 + 1")
                polyDictDenom1 = prbs.polyTreater (list1)
                polyDictSeed1 = {0:1, 1:1, 2:1, 3:1}
                self.data[i] = prbs.prbsGetter(i, polyDictDenom1, polyDictSeed1 )
           
        self.update(signal=True)

        
    def process(self, display=True):
        #Create meta array from updated data
        out_data = metaarray.MetaArray(self.data, info=[{'name': 'Time', 'values': np.linspace(0, len(self.data), len(self.data))}, {}])
        #Set outputs
        return {'Out': out_data}


class VCONode(CtrlNode):
    """Node Voltage Controlled Oscillator VCO that generates carrier waveform,
    frequency of which is controlled by input voltage.
    ToDo: If there is nothing connected to input, should generate nominal frequency carrier (presently nothing)"""
    
    nodeName = 'VCO'

    uiTemplate = [
        ('fd kHz/V', 'spin', {'values': 100, 'step': 1, 'range': [0, 200]})
    ]
	
    def __init__(self, name):
        terminals = {
            'In': dict(io='in', optional=False), #optional=True: operates although this terminal is not connected, however no output?.
            'Out': dict(io='out'),
        }
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, In, display=True):
        indata = In.asarray()
        fd = self.ctrls['fd kHz/V'].value()
        output = []
        summ = 0.0
        for i in range (0,global_data.BUFFER_SIZE):
            summ += indata[i]
            output.append( np.cos((2*1000*np.pi*i + 2*fd*np.pi*summ) / global_data.BUFFER_SIZE) )

        # Generate meta array for output
        out_data = metaarray.MetaArray(output, info=[{'name': 'Time', 'values': np.linspace(0, len(output), len(output))}, {}])

        return {'Out': out_data}


class RectifierNode(CtrlNode):
    """Rectifier Node"""
    nodeName = 'Rectifier'

    uiTemplate = [
        ('wave mode', 'combo', {'values': ['half', 'full'], 'index': 0})
    ]

    def __init__(self, name):
        terminals = {
            'In': dict(io='in'),
            'Out': dict(io='out'),
        }
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, In, display=True):
        # Read GUI parameter values
        mode = self.ctrls['wave mode'].currentText()

        data = In.asarray()

        if mode == "half":
            output = np.clip(data, 0, 100000)
        else:
            output = np.absolute(data)

        # Generate meta array for output
        out_data = metaarray.MetaArray(output, info=[{'name': 'Time', 'values': np.linspace(0, len(output), len(output))}, {}])

        return {'Out': out_data}

class DCBlockNode(CtrlNode):
    """Node that calculates and subtracts the average of the data"""

    nodeName = 'DCBlock'

    def __init__(self, name):
        terminals = {
            'In': dict(io='in'),
            'Out': dict(io='out'),
        }
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, In, display=True):
        data = In.asarray()
        mean = np.mean(data)
        output = np.subtract(data, mean)

        # Generate meta array for output
        out_data = metaarray.MetaArray(output, info=[{'name': 'Time', 'values': np.linspace(0, len(output), len(output))}, {}])

        return {'Out': out_data}


class OscilloscopeNode(Node):
    """Node that creates a new Oscilloscope widget and outputs data to it"""
    """ Bugs: Display remains when input is disconnected"""
    nodeName = 'Oscilloscope'

    def __init__(self, name):
        Node.__init__(self, name, terminals={'In1': {'io':'in'}, 'In2': {'io':'in'}})

        #Create an oscilloscope
        self.osc_widget = Oscilloscope()

        # Create and and a new dock on top of tools and add oscilloscope to it
        self.dock = Dock(name)
        global_data.area.addDock(self.dock, 'above', global_data.tool_dock)
        self.dock.addWidget(self.osc_widget)

        # Create plots for both inputs
        self.plot_item_1 = self.osc_widget.pwidget.plot()
        self.plot_item_2 = self.osc_widget.pwidget2.plot()

    # Update oscilloscope data signals based on input
    def process(self, In1, In2, display=True):
        if In1 is not None:
            self.plot_item_1.setData(In1)
        if In2 is not None:
            self.plot_item_2.setData(In2)

class CharToBinaryNode(Node):
    # adi edit: description of node changed:
    """Node that outputs the parameter character as 7-bit ASCII + eighth zero bit characters"""
    nodeName = 'CharToBinary'
    init_character = 'A'

    def __init__(self, name):
        ## Initialize node with only a single output terminal
        Node.__init__(self, name, terminals={'Out': {'io':'out'}})#,'In': {'io': 'in'}
        self.char = self.init_character
        self.update(signal=True)

    def set_character(self, char):
        # print("Changed character to " + char)
        self.char = char
        self.update(signal=True)

    #def process(self, In, display=True):
    def process(self, display=True):
        #if text is empty set bits to zero
        if self.char == "":
            result = [0, 0, 0, 0, 0, 0, 0, 0]
            data = metaarray.MetaArray(result, info=[{'name': 'Time', 'values': np.linspace(0, 7, len(result))}, {}])

        else:
            #Convert character to binary
            bin_value = bin(ord(str(self.char)))
            bin_list = list(bin_value[2:]) # remove '0b' from start and convert to array
            bin_array = [int(i) for i in bin_list] #Convert string list to int list
            if len (bin_array) == 6: #adi edit to account for characters with 6 bit binary code
                bin_array.insert(0, 0)#adi edit
            bin_array.insert(7, 0) #adi edit this eighth bit is actually kept for parity

            wholeoutput = []   # adi edit ins START
            for j in range(0, (global_data.BUFFER_SIZE-global_data.BUFFER_SIZE%8)/8): #(global_data.BUFFER_SIZE-global_data.BUFFER_SIZE%8)/8:
                for k in range(0,8): 
                    wholeoutput.append(bin_array[k])
            data = metaarray.MetaArray(wholeoutput, info=[{'name': 'Time', 'values': np.linspace(0, len(wholeoutput), len(wholeoutput))}, {}])
           # adi edit ins END
           
        return {'Out': data}

    def ctrlWidget(self):  # this method is optional
        text_field = QtGui.QLineEdit(self.init_character)
        text_field.setMaxLength(1)
        text_field.textEdited.connect(self.set_character)
        return text_field

class ParityNode(CtrlNode):
    """Node that appends a parity bit to binary sequence given as input"""
    nodeName = 'Parity'

    uiTemplate = [
        ('Parity', 'combo', {'values': ['even', 'odd'], 'index': 0})
    ]

    def __init__(self, name):
        terminals = {
            'In': dict(io='in'),
            'Out': dict(io='out'),
        }
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, In, display=True):
        # Read GUI parameter values
        parity = self.ctrls['Parity'].currentText()

        #data = In.view(np.ndarray)
        data = In.asarray()


        #adi edit - comments:
        #Desired changes in the 'Parity Bit Node':
        #Earlier version assumes that the input is 7-bit or 6-bit
        #(basically less than 8-bit) and appends an eighth bit

        #New version has "8-bit repeat sequence" input of which eighth bit (zero) has no meaning.
        #first seven bits of the sequence have to be retained, parity bit added, sequence repeated

        output = []

        
        # copy received data to output array
        for i in range(0,7): 
            output.append(data.item(i)) #copying seven bits from charToBinary node

        # append parity bit
        if parity == "odd":
            #if sum(data) % 2 == 0:  earlier version
            if sum(output) % 2 == 0:
                output.append(1)
            else:
                output.append(0)
        else:
            if sum(output) % 2 == 0:
                output.append(0)
            else:
                output.append(1)
        # Generate meta array for output
        wholeoutput = []
        for j in range(0,(global_data.BUFFER_SIZE-global_data.BUFFER_SIZE%8)/8): 
            for k in range(0,8): 
                wholeoutput.append(output[k])
        out_data = metaarray.MetaArray(wholeoutput, info=[{'name': 'Time', 'values': np.linspace(0, len(wholeoutput), len(wholeoutput))}, {}])

        return {'Out': out_data}

class CheckParityNode(CtrlNode):
    """Node that checks the integrity of data using the last bit as parity bit"""
    nodeName = 'CheckParity'
    uiTemplate = [
        ('Parity', 'combo', {'values': ['even', 'odd'], 'index': 0})
    ]

    def __init__(self, name):
        terminals = {
            'In': dict(io='in'),
            'Out': dict(io='out'),
        }
        CtrlNode.__init__(self, name, terminals=terminals)

        # Create a display widget
        self.widget = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        self.widget.setLayout(layout)
        self.status_widget = QtGui.QLabel("Status")
        layout.addWidget(self.status_widget)

        # Create and and a new dock on top of tools and add the display widget to it
        self.dock = Dock(name)
        global_data.area.addDock(self.dock, 'above', global_data.tool_dock)
        self.dock.addWidget(self.widget)

    def process(self, In, display=True):
        # Read GUI parameter values
        parity = self.ctrls['Parity'].currentText()

        data = In.asarray()

        if parity == "even":
            if sum(data) % 2 == 0:
                self.status_widget.setText("Message ok")
            else:
                self.status_widget.setText("Message incorrect")
        else:
            if sum(data) % 2 == 1:
                self.status_widget.setText("Message ok")
            else:
                self.status_widget.setText("Message incorrect")

        return {'Out': In}

class FFTNode(CtrlNode):
    """Node that performs FFT for 1 dimensional data array"""
    nodeName = 'FFT'

    def __init__(self, name):
        terminals = {
            'In': dict(io='in'),
            'Out': dict(io='out'),
        }
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, In, display=True):
        # Calculate FFT from input and calculate absolute values from complex values
        output = np.absolute(np.fft.fft(In.asarray()))

        # Generate MetaArray
        out_data = metaarray.MetaArray(output, info=[{'name': 'Time', 'values': np.linspace(0, len(output), len(output))}, {}])
        return {'Out': out_data}


class SigGenNode(CtrlNode):
    """Node that generates signals of different types"""
    nodeName = 'SigGen'
    uiTemplate = [
        ('waveform source', 'combo', {'values': ['None', 'ROT 0', 'ROT 1'], 'index': 0}),
        ('waveform', 'combo', {'values': ['sine', 'cosine', 'rectangular', 'sawtooth', 'noise', 'DC', 'Carrier', 'Carrier 90deg'], 'index': 0}),
        ('amplitude source', 'combo', {'values': ['None', 'POT 0', 'POT 1', 'POT 2', 'POT 3'], 'index': 0}),
        ('amplitude V',  'spin', {'value': 1.0, 'step': 0.01, 'range': [0.01, 10.0]}),
        ('frequency source', 'combo', {'values': ['None', 'POT 0', 'POT 1', 'POT 2', 'POT 3'], 'index': 0}),
        ('frequency kHz',  'spin', {'value': 10.0, 'step': 0.01, 'range': [0.01, 10.0]}),
        ('sawtooth shape',  'spin', {'value': 1.0, 'step': 0.01, 'range': [0.01, 1.0]})
    ]

    def __init__(self, name):
        terminals = {
            'Out': dict(io='out')
        }
        CtrlNode.__init__(self, name, terminals=terminals)

        self.data_size = global_data.BUFFER_SIZE
        self.batch_size = self.data_size #/ 10 # Update the whole signal buffer at once
        self.block_count = self.data_size / self.batch_size
        self.data = [0] * self.data_size  # Signal data buffer

        # Create and init update timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateSignal)
        self.timer.start(global_data.UPDATE_INTERVAL)

        # Pointer points to the value that will be updated next
        self.pointer = 0

    def updateSignal(self):
        # Get parameter values from GUI

        waveform_source = self.ctrls['waveform source'].currentText()
        amplitude_source = self.ctrls['amplitude source'].currentText()
        frequency_source = self.ctrls['frequency source'].currentText()
        sawtooth_shape = self.ctrls['sawtooth shape'].value()

        # Read amplitude
        if amplitude_source == "None":
            amplitude = self.ctrls['amplitude V'].value()
        else:
            knob_index = int(amplitude_source[len(amplitude_source)-1])  # Read the last character
            amplitude = global_data.potentiometer_values[knob_index] / 25.0  # Scale from [0,100] to [0,4]
            self.ctrls['amplitude V'].setValue(amplitude)

        # Read frequency in kHz
        if frequency_source == "None":
            frequency = self.ctrls['frequency kHz'].value()
        else:
            knob_index = int(frequency_source[len(frequency_source)-1])  # Read the last character
            frequency = global_data.potentiometer_values[knob_index] / 25.0  # Scale from [0,100] to [0,4]
            self.ctrls['frequency kHz'].setValue(frequency)

        # Change selected waveform if waveform source is enabled
        if waveform_source != "None":
            rot_index = int(waveform_source[len(waveform_source)-1])
            rot_value = global_data.rotatory_values[rot_index]
            self.ctrls['waveform'].setCurrentIndex(rot_value)

        waveform = self.ctrls['waveform'].currentText()


        #Rename the node to correspond the wave type
        #self.rename(waveform + " generator")

        # Update the signal buffer array depending on the wave type
        for i in range(self.data_size/self.block_count):
            index = self.pointer * self.data_size/self.block_count + i
            if waveform == 'sine':
                self.data[index] = amplitude * np.sin(index*2*np.pi*frequency/self.data_size)
            elif waveform == 'cosine':
                self.data[index] = amplitude * np.cos(index*2*np.pi*frequency/self.data_size)
            elif waveform == 'noise':
                self.data[index] = np.random.normal(scale=amplitude)
            elif waveform == 'rectangular':
                self.data[index] = amplitude * scipy.signal.square(2*np.pi*frequency*index/self.data_size)
            elif waveform == 'sawtooth':
                self.data[index] = amplitude * scipy.signal.sawtooth(2*np.pi*frequency*index/self.data_size,width=sawtooth_shape)
            elif waveform == 'DC':
                self.data[index] = amplitude * np.cos(0)
            elif waveform == 'Carrier':
                self.data[index] = np.cos(2*1000*np.pi*index/self.data_size)
            elif waveform == 'Carrier 90deg':
                self.data[index] = np.cos(2*1000*np.pi*index/self.data_size+np.pi/2)

        # move pointer
        self.pointer += 1

        # Hop to start if we have reached the end
        if self.pointer >= self.block_count:
            self.pointer = 0

        #Force the update of output values
        self.update(signal=True)

    def process(self, display=True):
        #Create meta array from updated data
        out_data = metaarray.MetaArray(self.data, info=[{'name': 'Time', 'values': np.linspace(0, len(self.data), len(self.data))}, {}])
        #Set outputs
        return {'Out': out_data}

class LineEncoderNode(CtrlNode):
    """Node that repeats symbol value many times over symbol duration or decodes it using specific coding"""
	    #When the whole signal buffer represents 1 ms period, rate defines sumbol rate in kBauds.
    nodeName = 'LineEncoder'
    uiTemplate = [
        ('code', 'combo', {'values': ['NRZ', 'Bipolar NRZ'], 'index': 0}),
        ('rate, kBaud',  'spin', {'value': 10, 'step': 1, 'range': [2, 100]}),
        ('decode mode', 'check', {'checked': False})
    ]
    def __init__(self, name):
        terminals = {
            'In': dict(io='in'),
            'Out': dict(io='out'),
        }
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, In, display=True):
        #Read parameter values
        code = self.ctrls['code'].currentText()
        symbolduration = global_data.BUFFER_SIZE / int(self.ctrls['rate, kBaud'].value())
        decode = self.ctrls['decode mode'].isChecked()

        indata = In.asarray()
        data = []
        #How many symbols fit into the array or buffer and take as many from indata to data
        for i in range (0,(global_data.BUFFER_SIZE-global_data.BUFFER_SIZE%symbolduration)/symbolduration):
            data.append(indata[i])
        
        output = []

        # duplicate each bit symbolduration times
        if not decode:
            if code == 'NRZ':
                for i in range(0, len(data)):
                    for j in range(0,symbolduration):
                        output.append(data[i])
            elif code == 'Bipolar NRZ':
                for i in range(0, len(data)):
                    for j in range(0,symbolduration):
                        if data.item(i) == 1:
                            signal_value = 0.5
                        else:
                            signal_value = -0.5
                        output.append(signal_value)
        # Decode with symbolduration, take mid value (if symbolduration=10, read values, 5+15+25etc.)
        else:
            if code == 'NRZ':
                for i in range(0, len(data)/symbolduration):
                    index = i * symbolduration + symbolduration / 2
                    output.append(data.item(index))
            elif code == 'Bipolar NRZ':
                for i in range(0, len(data)/symbolduration):
                    index = i * symbolduration + symbolduration / 2
                    value = data.item(index)
                    if value > 0:
                        output.append(1)
                    else:
                        output.append(0)

        #Generate MetaArray
        out_data = metaarray.MetaArray(output, info=[{'name': 'Time', 'values': np.linspace(0, len(output), len(output))}, {}])
        return {'Out': out_data}

class AmplifierNode(CtrlNode):
    """Node that amplifies or attenuates the signal"""
    nodeName = 'Amplifier'
    uiTemplate = [
        ('factor',  'spin', {'value': 1.0, 'step': 0.001, 'range': [0.0, 10.0]}),
        ('factor source', 'combo', {'values': ['None', 'Knob 0', 'Knob 1', 'Knob 2', 'Knob 3'], 'index': 0})
    ]
    def __init__(self, name):
        terminals = {
            'In': dict(io='in'),
            'Out': dict(io='out'),
        }
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, In, display=True):
        #Read parameter values
        factor = self.ctrls['factor'].value()
        factor_source = self.ctrls['factor source'].currentText()

        # Read value from controller knob
        if factor_source != "None":
            knob_index = int(factor_source[len(factor_source)-1])  # Read the last character
            factor = global_data.potentiometer_values[knob_index] / 25.0  # Scale from [0,100] to [0,4]
            self.ctrls['factor'].setValue(factor)

        # Amplify / attenuate
        output = factor * In.asarray()

        #Generate MetaArray
        out_data = metaarray.MetaArray(output, info=[{'name': 'Time', 'values': np.linspace(0, len(output), len(output))}, {}])
        return {'Out': out_data}

class FilterNode(CtrlNode):
    """Node that filters the signal"""
    nodeName = 'Filter'
    uiTemplate = [
        ('type', 'combo', {'values': ['LPF', 'HPF', 'BPF'], 'index': 0}),
        ('fh-3dB',  'spin', {'value': 10, 'step': 0.1, 'range': [0.0, 1000.0]}),
        ('fl-3dB',  'spin', {'value': 10, 'step': 0.1, 'range': [0.0, 1000.0]})
        
    ]
    def __init__(self, name):
        terminals = {
            'In': dict(io='in'),
            'Out': dict(io='out'),
        }
        CtrlNode.__init__(self, name, terminals=terminals)

    def process(self, In, display=True):
        # Read parameter values
        f_high_cutoff = self.ctrls['fh-3dB'].value()
        f_low_cutoff = self.ctrls['fl-3dB'].value()
        type = self.ctrls['type'].currentText()
        
        # Compute complex spectrum by fft for input signal of the filter
        fft_data = np.fft.fft(In.asarray())
        # Generate complex filter function, initially all are set to zero
        filter_func_complex = np.zeros(global_data.BUFFER_SIZE, dtype=np.complex_)
        #Needed variables are defined in each loop to make formulas shorter and computing faster
        if type == "LPF":
            for i in range(0, global_data.BUFFER_SIZE/2-1):
                i_fh = i/f_high_cutoff
                filter_func_complex[i] = 1.0 / (1.0 + np.power(i_fh, 2)) + ((-i_fh)/(1.0 + np.power(i_fh, 2))) * 1j
            for i in range(global_data.BUFFER_SIZE/2, global_data.BUFFER_SIZE-1):
                #Note that in this section frequency index (i-global_data.BUFFER_SIZE) is negative that changes complex filter function to conjugate of positive portion above.
                #This transferres frequencies close to global_data.BUFFER_SIZE to negative frequencies and the same filtering function can e used
                ig_fh = (i-global_data.BUFFER_SIZE) / f_high_cutoff
                filter_func_complex[i] = 1.0 / (1.0 + np.power(ig_fh, 2)) - ig_fh/(1.0 + np.power(ig_fh, 2)) * 1j
        elif type == "HPF":
            for i in range(0, global_data.BUFFER_SIZE/2-1):
                i_fl = i/f_low_cutoff
                filter_func_complex[i] = (np.power(i_fl, 2)/(1.0 + np.power(i_fl, 2))) + ((i_fl)/(1.0 + np.power(i_fl, 2))) * 1j
            for i in range(global_data.BUFFER_SIZE/2, global_data.BUFFER_SIZE-1):
                ig_fl = (i-global_data.BUFFER_SIZE)/f_low_cutoff
                filter_func_complex[i] = (np.power(ig_fl, 2))/(1.0 + np.power(ig_fl, 2)) + (ig_fl/(1.0 + np.power(ig_fl, 2))) * 1j
        elif type == "BPF":
            for i in range(0, global_data.BUFFER_SIZE/2-1):
                i_fl = i/f_low_cutoff
                i_fh = i/f_high_cutoff
                filter_func_complex[i] = ((np.power(i_fl, 2))+(i_fh)*(i_fl))/((1.0 + np.power(i_fh, 2))*(1.0 + np.power(i_fl, 2))) + ((i_fl)-(i_fh)* np.power(i_fl, 2))/((1.0 + np.power(i_fh, 2))*(1.0 + np.power(i_fl, 2))) * 1j    
            for i in range(global_data.BUFFER_SIZE/2, global_data.BUFFER_SIZE-1):
                ig_fl = (i-global_data.BUFFER_SIZE)/f_low_cutoff
                ig_fh = (i-global_data.BUFFER_SIZE) / f_high_cutoff
                filter_func_complex[i] = ((np.power(ig_fl, 2))+ig_fh * ig_fl)/((1 + np.power(ig_fh, 2))*(1.0 + np.power(ig_fl, 2))) + (ig_fl - ig_fh* np.power(ig_fl, 2))/((1.0 + np.power(ig_fh, 2))*(1.0 + np.power(ig_fl, 2))) * 1j   
        #print "---"
        # Filter data with filter function (in frequncy domain)
        filtered_data = filter_func_complex * fft_data
        # Compute inverse fft to reconstruct time domain signal for filter output
        output = np.real(np.fft.ifft(filtered_data)) # Only real part to remove zero valued imaginary part

        # Generate MetaArray
        out_data = metaarray.MetaArray(output, info=[{'name': 'Time', 'values': np.linspace(0, len(output), len(output))}, {}])
        return {'Out': out_data}


# TODO
class BinaryToCharNode(Node):
    """Node that converts a 7-bit ASCII character to a character and displays it"""
    nodeName = 'BinaryToChar'
    init_character = 'A'

    def __init__(self, name):
        ## Initialize node with only a single output terminal
        Node.__init__(self, name, terminals={'Out': {'io':'out'}})#,'In': {'io': 'in'}
        self.char = self.init_character
        self.update(signal=True)

    def set_character(self, char):
        # print("Changed character to " + char)
        self.char = char
        self.update(signal=True)

    #def process(self, In, display=True):
    def process(self, display=True):
        #if text is empty set bits to zero
        if self.char == "":
            result = [0, 0, 0, 0, 0, 0, 0, 0]
            data = metaarray.MetaArray(result, info=[{'name': 'Time', 'values': np.linspace(0, 7, len(result))}, {}])

        else:
            #Convert character to binary
            bin_value = bin(ord(str(self.char)))
            bin_list = list(bin_value[2:]) # remove '0b' from start and convert to array
            bin_array = [int(i) for i in bin_list] #Convert string list to int list
            #print(bin_array)
            data = metaarray.MetaArray(bin_array, info=[{'name': 'Time', 'values': np.linspace(0, 7, len(bin_array))}, {}])
        return {'Out': data}

    def ctrlWidget(self):  # this method is optional
        text_field = QtGui.QLineEdit(self.init_character)
        text_field.setMaxLength(1)
        text_field.textEdited.connect(self.set_character)

        return text_field
