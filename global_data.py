from pyqtgraph.dockarea import *
from pyqtgraph.Qt import QtGui, QtCore

# Values from arduino controller
potentiometer_values = [0.0, 0.0, 0.0, 0.0]
button_values = [0, 0, 0, 0, 0, 0, 0, 0]
rotatory_values = [0, 0]

# Data size used when generating and plotting signals
BUFFER_SIZE = 10000
# Interval of data updates in milliseconds
UPDATE_INTERVAL = 100

# We create the tool dock here so we can add widgets to it from nodes constructors. To be able to define it here
# we hava to create the app here too (Before creating docks)
app = QtGui.QApplication([])
area = DockArea()
tool_dock = Dock("Tools", size=(200, 200))