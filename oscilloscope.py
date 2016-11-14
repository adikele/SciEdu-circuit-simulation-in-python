from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import global_data

class Oscilloscope(QtGui.QWidget):
    data_size = global_data.BUFFER_SIZE

    def __init__(self, parent=None):
        super(Oscilloscope, self).__init__(parent)

        #Set layout
        ## Create a grid layout to manage the widgets size and position
        layout = QtGui.QGridLayout()
        self.setLayout(layout)

        #Create graph widget
        self.pwidget = pg.PlotWidget()
        self.pwidget2 = pg.PlotWidget()

        #Create the plot
        self.plot_item = self.pwidget.getPlotItem()
        self.plot_item2 = self.pwidget2.getPlotItem()
        # self.plot_curve = self.plot_item.plot(np.zeros(1000))
        # self.plot_item.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted

        # Hide auto scale button
        # self.plot_item.hideButtons()

        # Disable mouse zooming (Prints an error)
        # self.plot_item.getViewBox().setMouseEnabled(False,False)

        # Disable auto range
        self.plot_item.getViewBox().disableAutoRange()
        self.plot_item2.getViewBox().disableAutoRange()

        # Set labels
        self.plot_item.setLabel('left', text='Voltage')
        self.plot_item.setLabel('bottom', text='seconds')
        self.plot_item2.setLabel('left', text='Voltage')
        self.plot_item2.setLabel('bottom', text='seconds')

        # set starting range
        self.plot_item.getViewBox().setRange(xRange=(0, self.data_size), yRange=(-1, 1))
        self.plot_item2.getViewBox().setRange(xRange=(0, self.data_size), yRange=(-1, 1))

        # Set zoom limits
        # self.plotItem.getViewBox().setLimits(maxXRange=self.shared_data.signal_value_array_size,maxYRange=4)
        self.zoom_X = 1.0
        self.zoom_Y = 1.0
        self.zoom_level_x = 0
        self.zoom_level_y = 0

        # Add graph widget
        layout.addWidget(self.pwidget, 0, 1, 4, 8)
        layout.addWidget(self.pwidget2, 4, 1, 4, 8)

        # Add button widgets
        x_zoom_button = QtGui.QPushButton('X+')
        x_zoom_button.clicked.connect(self.zoom_x)
        layout.addWidget(x_zoom_button,8,3,1,1)

        x_zoom_out_button = QtGui.QPushButton('X-')
        x_zoom_out_button.clicked.connect(self.zoom_out_x)
        layout.addWidget(x_zoom_out_button,8,6,1,1)

        y_zoom_button = QtGui.QPushButton('Y+')
        y_zoom_button.clicked.connect(self.zoom_y)
        layout.addWidget(y_zoom_button,1,0,1,1)

        y_zoom_out_button = QtGui.QPushButton('Y-')
        y_zoom_out_button.clicked.connect(self.zoom_out_y)
        layout.addWidget(y_zoom_out_button,2,0,1,1)

        y_zoom_button = QtGui.QPushButton('Y+')
        y_zoom_button.clicked.connect(self.zoom_y2)
        layout.addWidget(y_zoom_button,5,0,1,1)

        y_zoom_out_button = QtGui.QPushButton('Y-')
        y_zoom_out_button.clicked.connect(self.zoom_out_y2)
        layout.addWidget(y_zoom_out_button,6,0,1,1)

    def zoom_x(self):
        self.zoom_level_x = self.zoom_level_x + 1
        self.plot_item.getViewBox().scaleBy(x=0.5)
        self.plot_item2.getViewBox().scaleBy(x=0.5)

    def zoom_out_x(self):
        if self.zoom_level_x >= 1:
            self.zoom_level_x = self.zoom_level_x - 1
            self.plot_item.getViewBox().scaleBy(x=2.0)
            self.plot_item2.getViewBox().scaleBy(x=2.0)

    def zoom_y(self):
        self.plot_item.getViewBox().scaleBy(y=0.5)

    def zoom_out_y(self):
        self.plot_item.getViewBox().scaleBy(y=2.0)

    def zoom_y2(self):
        self.plot_item2.getViewBox().scaleBy(y=0.5)

    def zoom_out_y2(self):
        self.plot_item2.getViewBox().scaleBy(y=2.0)

