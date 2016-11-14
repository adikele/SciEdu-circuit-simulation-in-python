"""
 Science Edu Tools
 Copyright Joni Anttalainen 2015, Tarmo Anttalainen 2015
 Copyright Aditya Kelekar 2016: PRBS Node

 This program uses Python 2.7 and requires the following packages:
 pyqtgraph (that requires numpy, scipy, PyQt4 or PySide), pyserial
"""

#import pyqtgraph and qt stuff
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pyqtgraph.dockarea import *
from pyqtgraph.flowchart import Flowchart
import pyqtgraph.flowchart.library as fclib

#import other necessary stuff
import os  # for paths etc
from PyQt4 import QtWebKit  # For QWebView
from functools import partial  # For freezing of function parameters

#import own python files
import global_data
from controller_widget import ControllerWidget
from data_structures import AssignmentGroup
from data_structures import Assignment
from data_structures import Exercise

# from oscilloscope import Oscilloscope
from nodes import OscilloscopeNode
from nodes import FilterNode
from nodes import RectifierNode
from nodes import DCBlockNode
from nodes import CharToBinaryNode
from nodes import BinaryToCharNode
from nodes import ParityNode
from nodes import CheckParityNode
from nodes import FFTNode
from nodes import SigGenNode
from nodes import LineEncoderNode
from nodes import AmplifierNode
from nodes import VCONode
from nodes import BinDataSourceNode
from nodes import PRBSNode

#define constants
WINDOW_DEFAULT_WIDTH = 1000
WINDOW_DEFAULT_HEIGHT = 500
VERSION_ID = '0.21b'

#define variables

#################################
# Load assignment data into variables
#################################
assignment_groups = []

# Loop through assignment group folders until they don't exist anymore, starting from "assignments/1"
directory_was_found = True
counter = 0
while directory_was_found:
    counter += 1
    assignment_group_path = "content" + os.sep + "groups" + os.sep + str(counter)
    # print 'Checking for existance of ' + assignment_group_path
    directory_was_found = os.path.isdir(assignment_group_path)
    if directory_was_found:
        # print 'It exists!'
        # Read assignment groups metadata from a file
        metadata_path = assignment_group_path + os.sep + "METADATA"
        with open(metadata_path) as f:
            content = f.readlines()
        for line in content:
            if line.split('|')[0] == "NAME":
                assignment_group_name = line.split('|')[1].rstrip()
            elif line.split('|')[0] == "DESCRIPTION":
                assignment_group_description = line.split('|')[1].rstrip()
        # Create new assignment group
        new_assignment_group = AssignmentGroup(name=assignment_group_name, description=assignment_group_description)

        # Append assignments to assignment group by looping
        assignment_counter = 0
        assignment_was_found = True
        while assignment_was_found:
            assignment_counter += 1
            assignment_path = "content"+os.sep+"groups"+os.sep+str(counter)+os.sep+str(assignment_counter)
            # print 'Checking for existance of ' + assignment_path
            assignment_was_found = os.path.isdir(assignment_path)
            if assignment_was_found:
                # print 'It exists!'
                # Read assignments metadata from file
                metadata_path = assignment_path + os.sep + "METADATA"
                with open(metadata_path) as f:
                    content = f.readlines()
                for line in content:
                    if line.split('|')[0] == "NAME":
                        assignment_name = line.split('|')[1].rstrip()
                    elif line.split('|')[0] == "DESCRIPTION":
                        assignment_description = line.split('|')[1].rstrip()
                new_assignment = Assignment(name=assignment_name, description=assignment_description, background_url=assignment_path+os.sep+"background.html")
                # similarly loop through exercises
                exercise_counter = 0
                exercise_was_found = True
                while exercise_was_found:
                    exercise_counter += 1
                    exercise_path = "content"+os.sep+"groups"+os.sep+str(counter)+os.sep+str(assignment_counter)+os.sep+str(exercise_counter)
                    # print 'Checking for existance of ' + exercise_path
                    exercise_was_found = os.path.isdir(exercise_path)
                    if exercise_was_found:
                        # print 'It exists!'
                        # Read assignments metadata from file
                        metadata_path = exercise_path + os.sep + "METADATA"
                        with open(metadata_path) as f:
                            content = f.readlines()
                        for line in content:
                            if line.split('|')[0] == "NAME":
                                exercise_name = line.split('|')[1].rstrip()
                            elif line.split('|')[0] == "DESCRIPTION":
                                exercise_description = line.split('|')[1].rstrip()
                        new_exercise = Exercise(name=exercise_name, description=exercise_description, instructions_url=exercise_path+os.sep+"instructions.html")
                        new_assignment.exercises.append(new_exercise)
                new_assignment_group.assignments.append(new_assignment)
        assignment_groups.append(new_assignment_group)

# Print the assignment tree
#print "Loaded file structure:"
#for group in assignment_groups:
#    print "Group name: " + group.name + ", description: " + group.description
#    for assignment in group.assignments:
#        print "\tAssignment name: " + assignment.name + ", description: " + assignment.description + ", background path: " + assignment.background_url
#        for exercise in assignment.exercises:
#            print "\t\tExercise name: " + exercise.name + ", description: " + exercise.description + ", instructions path: " + exercise.instructions_url

##################################
# End of data loading
##################################

# Init current exercise
current_assignment_group = assignment_groups[0]
current_assignment = current_assignment_group.assignments[0]
current_exercise = current_assignment.exercises[0]

# Begin PyQtGraph application

#app = QtGui.QApplication([])
win = QtGui.QMainWindow()
#area = DockArea()
win.setCentralWidget(global_data.area)
#win.showFullScreen()
#win.showMaximized()
win.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)

# Exercise name label
label = QtGui.QLabel(current_exercise.name)

# Create fixed docks
ex_info = Dock("Instructions")  # give this dock the minimum possible size
background_info = Dock("Background")
controller = Dock("Controller")
d3 = Dock("Node Controls")
flowchart_dock = Dock("Connections")

# Place docks on screen
global_data.area.addDock(ex_info, 'left')
global_data.area.addDock(background_info, 'above', ex_info)
global_data.area.addDock(d3, 'right', ex_info)
global_data.area.addDock(controller, 'bottom', d3)
global_data.area.addDock(global_data.tool_dock, 'right')
global_data.area.addDock(flowchart_dock, 'bottom', global_data.tool_dock)

## Add widgets into each dock

# Add instructions widget for exercise
instructions = QtWebKit.QWebView()
# add the widget to a slot on the window
w1 = pg.LayoutWidget()
w1.addWidget(instructions, row=2, col=0)
ex_info.addWidget(w1)

# Add background widget for assignment
background = QtWebKit.QWebView()
background_info.addWidget(background)

## restore button
restoreBtn = QtGui.QPushButton('Restore default view')
restoreBtn.setEnabled(False)
w1.addWidget(label, row=0, col=0)
w1.addWidget(restoreBtn, row=3, col=0)

state = None


# Save view state
def save():
    global state
    state = global_data.area.saveState()
    restoreBtn.setEnabled(True)


# Load view state
def load():
    global state
    global_data.area.restoreState(state)

restoreBtn.clicked.connect(load)

# Save the default state of view of main window
save()

# Create and Add a ControllerWidget (for visual and serial communication)
controller_w = ControllerWidget()
controller.addWidget(controller_w)

#####################################
# Create Flow Chart and components
#####################################

# Create flowchart, define input/output terminals
fc = Flowchart(terminals={
    #'sigOut': {'io': 'in'},
    #'sigOut2': {'io': 'in'}#,
    #'sigIn': {'io': 'out'}  #We don't currently need any outputs from FC
}, name='Connections')

# Remove the unnecessary input and output nodes
fc.removeNode(fc.inputNode)
fc.removeNode(fc.outputNode)

flowchart = fc.widget()
d3.addWidget(flowchart)
flowchart_dock.addWidget(fc.widget().chartWidget)

#Register own node types
fclib.registerNodeType(OscilloscopeNode, [('SciEdu',)])
fclib.registerNodeType(FilterNode, [('SciEdu',)])
fclib.registerNodeType(CharToBinaryNode, [('SciEdu',)])
# fclib.registerNodeType(BinaryToCharNode, [('SciEdu',)]) # TODO
fclib.registerNodeType(ParityNode, [('SciEdu',)])
fclib.registerNodeType(CheckParityNode, [('SciEdu',)])
fclib.registerNodeType(FFTNode, [('SciEdu',)])
fclib.registerNodeType(SigGenNode, [('SciEdu',)])
fclib.registerNodeType(AmplifierNode, [('SciEdu',)])
fclib.registerNodeType(LineEncoderNode, [('SciEdu',)])
fclib.registerNodeType(RectifierNode, [('SciEdu',)])
fclib.registerNodeType(DCBlockNode, [('SciEdu',)])
fclib.registerNodeType(VCONode, [('SciEdu',)])
fclib.registerNodeType(BinDataSourceNode, [('SciEdu',)])
fclib.registerNodeType(PRBSNode, [('SciEdu',)])

# Test thread generation (Not in use now)
#import time

#class WorkThread(QtCore.QThread):
#    def __init__(self, node):
#        QtCore.QThread.__init__(self)
#        self.node = node

#    def __del__(self):
#        self.wait()

#    def run(self):
#        running = True
#        print("update ")
#        while running:
#            self.node.updateSignal()
#            time.sleep(0.0001)
        #Exiting thread now, work is finished
        #self.terminate() # not necessary
#wt = WorkThread(signal)
#wt.start()

#Find all signals and update them TODO
#def updateSignals():
    #nodes = fc.nodes()
    #for node in nodes:
    #    if nodes[node.nodeName] == 'SigGen':
    #        nodes[node.nodeName].updateSignal()
#    signal1.updateSignal()
#    signal2.updateSignal()

#Create and init update timer
#timer = QtCore.QTimer()
#timer.timeout.connect(updateSignals)
#timer.start(10)

# Create and add oscilloscope 1
#osc = Oscilloscope()
#d4.addWidget(osc)
# Add a plotwidget for it to FC
#osc_node = fc.createNode('PlotWidget', name='Oscilloscope 1', pos=(100, 100))
# Connect the node data to osc's plot
#osc_node.setPlot(osc.pwidget)

# Create and add oscilloscope 2
# Add a plotwidget for it to FC
#osc_node2 = fc.createNode('PlotWidget', name='Oscilloscope 2', pos=(100, -100))
# Connect the node data to osc's plot
#osc_node2.setPlot(osc.pwidget2)

# Create pre-made connections (Might not be necessary for most exercises)
#fc.connectTerminals(fc['sigOut'], fftNode['In'])

#########################################
# End flow chart
#########################################

#########################################
# Start of group selection window
#########################################
# Create the load up screen where user selects the group and assignment
load_window = QtGui.QMainWindow()
load_area = DockArea()
load_window.resize(WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
load_window.setWindowTitle('Sci edu ' + VERSION_ID)

# Create group selection widget
group_selection_widget = QtGui.QWidget()

load_group_label = QtGui.QLabel('Welcome to SciEdu ' + VERSION_ID + '! Please select the group of assignments.')
load_assignment_label = QtGui.QLabel('Please select the assignment.')

group_selection_layout = QtGui.QGridLayout()


# Generate loading menu
def setup_group_selection():
    # Add content
    layout = QtGui.QGridLayout()
    layout.addWidget(load_group_label, 0, 0, 1, 2)

    # Add each group
    counter = 1
    for g in assignment_groups:
        button = QtGui.QPushButton(g.name)

        def load_group(group):
            print "Loading group " + group.name
            global current_assignment_group
            current_assignment_group = group
            group_widget = QtGui.QWidget()
            group_layout = QtGui.QGridLayout()

            # Add each assignment
            counter = 1
            for a in current_assignment_group.assignments:
                button = QtGui.QPushButton(a.name)
                # button press triggers update of instructions and background and shows the main window
                def load_assignment(assignment):
                    print "Loading assignment " + assignment.name

                    # Update current assignment and exercise
                    global current_assignment
                    current_assignment = assignment
                    global current_exercise
                    current_exercise = assignment.exercises[0]

                    # Load relevant instructions and background. Exercise 1 is loaded by default
                    instructions.load(QtCore.QUrl.fromLocalFile(os.getcwd() + os.sep + current_exercise.instructions_url))
                    background.load(QtCore.QUrl.fromLocalFile(os.getcwd() + os.sep + assignment.background_url))

                    # Update info label
                    label.setText(current_exercise.name + ': ' + current_exercise.description)

                    # Generate exercise drop down menu
                    menubar = win.menuBar()
                    exerciseMenu = menubar.addMenu('&Exercises')

                    # Add exercises to menu
                    for e in assignment.exercises:
                        load_exercise_action = QtGui.QAction(QtCore.QString(e.name), exerciseMenu)
                        load_exercise_action.setStatusTip('Load exercise ' + e.name)

                        # What happens when we load an exercise from the drop down menu
                        def loadExercise(ex):
                            #Set info label
                            label.setText(ex.name + ': ' + ex.description)
                            # Set instructions
                            instructions.load(QtCore.QUrl.fromLocalFile(os.getcwd() + os.sep + ex.instructions_url))
                            # Set window title
                            win.setWindowTitle('Sci edu ' + VERSION_ID + ": " + ex.name)

                        load_exercise_action.triggered.connect(partial(loadExercise, e))

                        exerciseMenu.addAction(load_exercise_action)
                    # fileMenu.addAction(exitAction)
                    viewMenu = menubar.addMenu('&View')
                    # fileMenu.addAction(exitAction)
                    helpMenu = menubar.addMenu('&Help')

                    # Hide load window and show main window
                    win.setWindowTitle('Sci edu ' + VERSION_ID + ": " + current_exercise.name)
                    #win.show()
                    win.showMaximized()
                    load_window.hide()
                button.clicked.connect(partial(load_assignment, a))
                global group_label
                group_label = QtGui.QLabel(a.description)
                group_layout.addWidget(button, counter, 0)
                group_layout.addWidget(group_label, counter, 1)
                counter += 1

            group_widget.setLayout(group_layout)
            load_window.setCentralWidget(group_widget)

        button.clicked.connect(partial(load_group, g))
        group_label = QtGui.QLabel(g.description)
        layout.addWidget(button, counter, 0)
        layout.addWidget(group_label, counter, 1)
        counter += 1
    #return layout
    global group_selection_layout
    group_selection_layout = layout

    # Set group selection widget to load windows content
    global group_selection_widget
    group_selection_widget.setLayout(group_selection_layout)

    global load_window
    load_window.setCentralWidget(group_selection_widget)

    load_window.showMaximized()

# at first init group selection
#group_selection_layout = setup_group_selection()

setup_group_selection()
# Set group selection widget to load windows content
#group_selection_widget.setLayout(group_selection_layout)
#load_window.setCentralWidget(group_selection_widget)

#########################################
# End of group selection window
#########################################


## assignment selection button
#changeAssignmentBtn = QtGui.QPushButton('Change assignment')
#changeAssignmentBtn.setEnabled(False) # TODO doesn't work
#w1.addWidget(changeAssignmentBtn, row=3, col=1)
#changeAssignmentBtn.clicked.connect(setup_group_selection)

# Show loading window
#load_window.show()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
