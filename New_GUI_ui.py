# PyQt4 can be downloaded from:
#   http://www.riverbankcomputing.com/software/pyqt/download
# PyQt4 requires Qt be installed.
# PyQt4 also requires that SIP be installed
#   http://www.riverbankcomputing.com/software/sip/download
#

from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import os

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, mainwindow):
        mainwindow.resize(900, 770) # Set default size of window, but it is resizable.
        mainwindow.setMaximumSize(QtCore.QSize(900, 770))
        # Create the scroll area: 
        self.scrollArea = QtGui.QScrollArea(mainwindow)
        mainwindow.setCentralWidget(self.scrollArea) # Set central widget so it expands to fill mainwindow.
        
        Form = QtGui.QWidget(self.scrollArea)
        Form.setGeometry(QtCore.QRect(0, 0, 900, 770)) # Form is a QWidget that contains the GUI
        self.scrollArea.setWidget(Form)
        
        self.stateobj = {} # Dictionary that stores references to each UI element
        
        Form.setStyleSheet('font-size: 10pt; font-family: Arial;')
        
        # Create pretty borders:
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(2, 15, 670, 753))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame1Label = QtGui.QLabel(Form)
        self.frame1Label.setGeometry(QtCore.QRect(10, 5, 200, 15))
        self.frame1Label.setAlignment(QtCore.Qt.AlignLeft)
        font = QtGui.QFont()
        font.setPixelSize(10)
        self.frame1Label.setFont(font)
        self.frame1Label.setText("Current Black Pulse Programmer State")
        
        self.frame2 = QtGui.QFrame(Form)
        self.frame2.setGeometry(QtCore.QRect(675, 15, 222, 753))
        self.frame2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame2Label = QtGui.QLabel(Form)
        self.frame2Label.setGeometry(QtCore.QRect(683, 5, 200, 15))
        self.frame2Label.setAlignment(QtCore.Qt.AlignLeft)
        self.frame2Label.setFont(font)
        self.frame2Label.setText("DAQ Settings")
        
        
        self.openButton = QtGui.QPushButton(Form)
        self.openButton.setGeometry(QtCore.QRect(0, 740, 71, 31))
        self.saveAsButton = QtGui.QPushButton(Form)
        self.saveAsButton.setGeometry(QtCore.QRect(70, 740, 81, 31))
        self.runButton = QtGui.QPushButton(Form)
        self.runButton.setGeometry(QtCore.QRect(150, 740, 61, 31))
        self.stopButton = QtGui.QPushButton(Form)
        self.stopButton.setGeometry(QtCore.QRect(210, 740, 71, 31))
        self.readoutButton = QtGui.QPushButton(Form)
        self.readoutButton.setGeometry(QtCore.QRect(280, 740, 81, 31))
        self.resetPlotButton = QtGui.QPushButton(Form)
        self.resetPlotButton.setGeometry(QtCore.QRect(360, 740, 91, 31))
        
        self.THRES0Box = QtGui.QDoubleSpinBox(Form)
        self.stateobj["THRES0"] = self.THRES0Box
        self.THRES0Box.setGeometry(QtCore.QRect(120, 230, 111, 31))
        self.THRES0Box.setRange(0, 100000)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.THRES0Box.setFont(font)
        
        self.SHUTRBox = QtGui.QSpinBox(Form)
        self.stateobj["SHUTR"] = self.SHUTRBox
        self.SHUTRBox.setGeometry(QtCore.QRect(120, 200, 111, 31))
        self.SHUTRBox.setRange(0, 100000)
        QtCore.QObject.connect(self.SHUTRBox, QtCore.SIGNAL("valueChanged(int)"), mainwindow.shutter_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.SHUTRBox.setFont(font)
        
        self.DDS4AmplitudeBox = QtGui.QSpinBox(Form)
        self.stateobj["DDS4_AMP"] = self.DDS4AmplitudeBox;
        self.DDS4AmplitudeBox.setGeometry(QtCore.QRect(230, 170, 111, 31))
        self.DDS4AmplitudeBox.dds_num = 4
        self.DDS4AmplitudeBox.setRange(0, 100000)
        QtCore.QObject.connect(self.DDS4AmplitudeBox, QtCore.SIGNAL("valueChanged(int)"), mainwindow.amp_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS4AmplitudeBox.setFont(font)
        
        self.DDS4PhaseBox = QtGui.QSpinBox(Form)
        self.stateobj["DDS4_PHASE"] = self.DDS4PhaseBox
        self.DDS4PhaseBox.setGeometry(QtCore.QRect(340, 170, 111, 31))
        self.DDS4PhaseBox.dds_num = 4
        self.DDS4PhaseBox.setRange(0, 100000)
        QtCore.QObject.connect(self.DDS4PhaseBox, QtCore.SIGNAL("valueChanged(int)"), mainwindow.phase_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS4PhaseBox.setFont(font)
        
        self.THRES1Box = QtGui.QDoubleSpinBox(Form)
        self.stateobj["THRES1"] = self.THRES1Box
        self.THRES1Box.setGeometry(QtCore.QRect(340, 230, 111, 31))
        self.THRES1Box.setRange(0, 100000)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.THRES1Box.setFont(font)
        
        self.CMDValueLabel = QtGui.QLabel(Form)
        self.CMDValueLabel.setGeometry(QtCore.QRect(120, 260, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.CMDValueLabel.setFont(font)
        self.CMDValueLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        self.DDS4FrequencyBox = QtGui.QDoubleSpinBox(Form)
        self.stateobj["DDS4_FREQ"] = self.DDS4FrequencyBox
        self.DDS4FrequencyBox.setGeometry(QtCore.QRect(120, 170, 111, 31))
        self.DDS4FrequencyBox.dds_num = 4
        self.DDS4FrequencyBox.setRange(0, 100000)
        QtCore.QObject.connect(self.DDS4FrequencyBox, QtCore.SIGNAL("valueChanged(double)"), mainwindow.freq_changed)
        self.DDS4FrequencyBox.setDecimals(4)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS4FrequencyBox.setFont(font)
        self.DDS4FrequencyBox.setSingleStep(0.1)
        
        self.DDS3FrequencyBox = QtGui.QDoubleSpinBox(Form)
        self.stateobj["DDS3_FREQ"] = self.DDS3FrequencyBox
        self.DDS3FrequencyBox.setGeometry(QtCore.QRect(120, 140, 111, 31))
        self.DDS3FrequencyBox.setDecimals(4)
        self.DDS3FrequencyBox.dds_num = 3
        self.DDS3FrequencyBox.setRange(0, 100000)
        QtCore.QObject.connect(self.DDS3FrequencyBox, QtCore.SIGNAL("valueChanged(double)"), mainwindow.freq_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS3FrequencyBox.setFont(font)
        self.DDS3FrequencyBox.setSingleStep(0.1)
        
        self.DDS2FrequencyBox = QtGui.QDoubleSpinBox(Form)
        self.stateobj["DDS2_FREQ"] = self.DDS2FrequencyBox
        self.DDS2FrequencyBox.setGeometry(QtCore.QRect(120, 110, 111, 31))
        self.DDS2FrequencyBox.setDecimals(4)
        self.DDS2FrequencyBox.dds_num = 2
        self.DDS2FrequencyBox.setRange(0, 100000)
        QtCore.QObject.connect(self.DDS2FrequencyBox, QtCore.SIGNAL("valueChanged(double)"), mainwindow.freq_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS2FrequencyBox.setFont(font)
        self.DDS2FrequencyBox.setSingleStep(0.1)
        
        self.DDS1FrequencyBox = QtGui.QDoubleSpinBox(Form)
        self.stateobj["DDS1_FREQ"] = self.DDS1FrequencyBox
        self.DDS1FrequencyBox.setGeometry(QtCore.QRect(120, 80, 111, 31))
        self.DDS1FrequencyBox.setDecimals(4)
        self.DDS1FrequencyBox.dds_num = 1
        self.DDS1FrequencyBox.setRange(0, 100000)
        QtCore.QObject.connect(self.DDS1FrequencyBox, QtCore.SIGNAL("valueChanged(double)"), mainwindow.freq_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS1FrequencyBox.setFont(font)
        self.DDS1FrequencyBox.setSingleStep(0.1)
        
        self.DDS0FrequencyBox = QtGui.QDoubleSpinBox(Form)
        self.stateobj["DDS0_FREQ"] = self.DDS0FrequencyBox
        self.DDS0FrequencyBox.setGeometry(QtCore.QRect(120, 50, 111, 31))
        self.DDS0FrequencyBox.setDecimals(4)
        self.DDS0FrequencyBox.dds_num = 0
        self.DDS0FrequencyBox.setRange(0, 100000)
        QtCore.QObject.connect(self.DDS0FrequencyBox, QtCore.SIGNAL("valueChanged(double)"), mainwindow.freq_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS0FrequencyBox.setFont(font)
        self.DDS0FrequencyBox.setSingleStep(0.1)
        
        self.DDS3PhaseBox = QtGui.QSpinBox(Form)
        self.stateobj["DDS3_PHASE"] = self.DDS3PhaseBox
        self.DDS3PhaseBox.setGeometry(QtCore.QRect(340, 140, 111, 31))
        self.DDS3PhaseBox.dds_num = 3
        self.DDS3PhaseBox.setRange(0, 100000)
        QtCore.QObject.connect(self.DDS3PhaseBox, QtCore.SIGNAL("valueChanged(int)"), mainwindow.phase_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS3PhaseBox.setFont(font)
        
        self.DDS3AmplitudeBox = QtGui.QSpinBox(Form)
        self.stateobj["DDS3_AMP"] = self.DDS3AmplitudeBox
        self.DDS3AmplitudeBox.setGeometry(QtCore.QRect(230, 140, 111, 31))
        self.DDS3AmplitudeBox.dds_num = 3
        self.DDS3AmplitudeBox.setRange(0, 100000)
        QtCore.QObject.connect(self.DDS3AmplitudeBox, QtCore.SIGNAL("valueChanged(int)"), mainwindow.amp_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS3AmplitudeBox.setFont(font)
        
        self.DDS2PhaseBox = QtGui.QSpinBox(Form)
        self.stateobj["DDS2_PHASE"] = self.DDS2PhaseBox
        self.DDS2PhaseBox.setGeometry(QtCore.QRect(340, 110, 111, 31))
        self.DDS2PhaseBox.dds_num = 2
        self.DDS2PhaseBox.setRange(0, 100000)
        QtCore.QObject.connect(self.DDS2PhaseBox, QtCore.SIGNAL("valueChanged(int)"), mainwindow.phase_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS2PhaseBox.setFont(font)
        
        self.DDS2AmplitudeBox = QtGui.QSpinBox(Form)
        self.stateobj["DDS2_AMP"] = self.DDS2AmplitudeBox
        self.DDS2AmplitudeBox.setGeometry(QtCore.QRect(230, 110, 111, 31))
        self.DDS2AmplitudeBox.setRange(0, 100000)
        self.DDS2AmplitudeBox.dds_num = 2
        QtCore.QObject.connect(self.DDS2AmplitudeBox, QtCore.SIGNAL("valueChanged(int)"), mainwindow.amp_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS2AmplitudeBox.setFont(font)
        
        self.DDS1PhaseBox = QtGui.QSpinBox(Form)
        self.stateobj["DDS1_PHASE"] = self.DDS1PhaseBox
        self.DDS1PhaseBox.setGeometry(QtCore.QRect(340, 80, 111, 31))
        self.DDS1PhaseBox.dds_num = 1
        self.DDS1PhaseBox.setRange(0, 100000)
        QtCore.QObject.connect(self.DDS1PhaseBox, QtCore.SIGNAL("valueChanged(int)"), mainwindow.phase_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS1PhaseBox.setFont(font)
        
        self.DDS1AmplitudeBox = QtGui.QSpinBox(Form)
        self.stateobj["DDS1_AMP"] = self.DDS1AmplitudeBox
        self.DDS1AmplitudeBox.setGeometry(QtCore.QRect(230, 80, 111, 31))
        self.DDS1AmplitudeBox.setRange(0, 100000)
        self.DDS1AmplitudeBox.dds_num = 1
        QtCore.QObject.connect(self.DDS1AmplitudeBox, QtCore.SIGNAL("valueChanged(int)"), mainwindow.amp_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS1AmplitudeBox.setFont(font)
        
        self.DDS0PhaseBox = QtGui.QSpinBox(Form)
        self.stateobj["DDS0_PHASE"] = self.DDS0PhaseBox
        self.DDS0PhaseBox.setGeometry(QtCore.QRect(340, 50, 111, 31))
        self.DDS0PhaseBox.dds_num = 0
        self.DDS0PhaseBox.setRange(0, 100000)
        QtCore.QObject.connect(self.DDS0PhaseBox, QtCore.SIGNAL("valueChanged(int)"), mainwindow.phase_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS0PhaseBox.setFont(font)
        
        self.DDS0AmplitudeBox = QtGui.QSpinBox(Form)
        self.stateobj["DDS0_AMP"] = self.DDS0AmplitudeBox
        self.DDS0AmplitudeBox.setGeometry(QtCore.QRect(230, 50, 111, 31))
        self.DDS0AmplitudeBox.dds_num = 0
        self.DDS0AmplitudeBox.setRange(0, 100000)
        QtCore.QObject.connect(self.DDS0AmplitudeBox, QtCore.SIGNAL("valueChanged(int)"), mainwindow.amp_changed)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS0AmplitudeBox.setFont(font)
        
        self.DATAValueLabel = QtGui.QLabel(Form)
        self.DATAValueLabel.setGeometry(QtCore.QRect(340, 260, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DATAValueLabel.setFont(font)
        self.DATAValueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.WValueLabel = QtGui.QLabel(Form)
        self.WValueLabel.setGeometry(QtCore.QRect(340, 290, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.WValueLabel.setFont(font)
        self.WValueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.THRES1Label = QtGui.QLabel(Form)
        self.THRES1Label.setGeometry(QtCore.QRect(230, 230, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.THRES1Label.setFont(font)
        self.THRES1Label.setAlignment(QtCore.Qt.AlignCenter)
        self.THRES0Label = QtGui.QLabel(Form)
        self.THRES0Label.setGeometry(QtCore.QRect(10, 230, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.THRES0Label.setFont(font)
        self.THRES0Label.setAlignment(QtCore.Qt.AlignCenter)
        self.PCValueLabel = QtGui.QLabel(Form)
        self.PCValueLabel.setGeometry(QtCore.QRect(120, 290, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.PCValueLabel.setFont(font)
        self.PCValueLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.CMDLabel = QtGui.QLabel(Form)
        self.CMDLabel.setGeometry(QtCore.QRect(10, 260, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.CMDLabel.setFont(font)
        self.CMDLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.PCLabel = QtGui.QLabel(Form)
        self.PCLabel.setGeometry(QtCore.QRect(10, 290, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.PCLabel.setFont(font)
        self.PCLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.DATALabel = QtGui.QLabel(Form)
        self.DATALabel.setGeometry(QtCore.QRect(230, 260, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DATALabel.setFont(font)
        self.DATALabel.setAlignment(QtCore.Qt.AlignCenter)
        self.WLabel = QtGui.QLabel(Form)
        self.WLabel.setGeometry(QtCore.QRect(230, 290, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.WLabel.setFont(font)
        self.WLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.DDS0Label = QtGui.QLabel(Form)
        self.DDS0Label.setGeometry(QtCore.QRect(10, 50, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS0Label.setFont(font)
        self.DDS0Label.setAlignment(QtCore.Qt.AlignCenter)
        self.DDS1Label = QtGui.QLabel(Form)
        self.DDS1Label.setGeometry(QtCore.QRect(10, 80, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS1Label.setFont(font)
        self.DDS1Label.setAlignment(QtCore.Qt.AlignCenter)
        self.DDS2Label = QtGui.QLabel(Form)
        self.DDS2Label.setGeometry(QtCore.QRect(10, 110, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS2Label.setFont(font)
        self.DDS2Label.setAlignment(QtCore.Qt.AlignCenter)
        self.DDS3Label = QtGui.QLabel(Form)
        self.DDS3Label.setGeometry(QtCore.QRect(10, 140, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS3Label.setFont(font)
        self.DDS3Label.setAlignment(QtCore.Qt.AlignCenter)
        self.DDS4Label = QtGui.QLabel(Form)
        self.DDS4Label.setGeometry(QtCore.QRect(10, 170, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.DDS4Label.setFont(font)
        self.DDS4Label.setAlignment(QtCore.Qt.AlignCenter)
        self.FrequencyLabel = QtGui.QLabel(Form)
        self.FrequencyLabel.setGeometry(QtCore.QRect(120, 20, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.FrequencyLabel.setFont(font)
        self.FrequencyLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.SHUTRLabel = QtGui.QLabel(Form)
        self.SHUTRLabel.setGeometry(QtCore.QRect(10, 200, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.SHUTRLabel.setFont(font)
        self.SHUTRLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.AmplitudeLabel = QtGui.QLabel(Form)
        self.AmplitudeLabel.setGeometry(QtCore.QRect(230, 20, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.AmplitudeLabel.setFont(font)
        self.AmplitudeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.PhaseLabel = QtGui.QLabel(Form)
        self.PhaseLabel.setGeometry(QtCore.QRect(340, 20, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.PhaseLabel.setFont(font)
        self.PhaseLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        # Create PyQtGraph graph
        pg.setConfigOption('background', 'w') # Switch to using white background and black foreground
        pg.setConfigOption('foreground', 'k')
        self.countsPlotWidget = pg.PlotWidget(Form, background='w') # Set the parent widget to be the Form window.
        self.countsPlotWidget.setGeometry(QtCore.QRect(3, 320, 447, 420))
        self.counts_graph = self.countsPlotWidget.getPlotItem()
        self.counts_graph.setTitle('Measured Counts Per Exp. and Occurrences of Measured Counts')
        self.counts_graph.showAxis('left', show=True)
        self.counts_graph.setLabel('left', text="Counts/Prob. Dist.")
        self.counts_graph.showAxis('bottom', show=True)
        self.counts_graph.setLabel('bottom', text="Measurement/Counts")
        self.counts_graph.showGrid(y=True, alpha=0.5)        
        
        # Create parameter table
        self.parameterTable = QtGui.QTableWidget(Form)
        self.parameterTable.setGeometry(QtCore.QRect(453, 15, 217, 752))
        self.parameterTable.setColumnCount(2)
        self.parameterTable.setRowCount(40)
        self.tableHeader = ["Parameter Name", "Value"]
        self.parameterTable.setHorizontalHeaderLabels(self.tableHeader)
        self.parameterTable.verticalHeader().setVisible(False)
        
        self.parameterTable.setColumnWidth(0,115)
        self.parameterTable.setColumnWidth(1,100)
        for i in range(0,self.parameterTable.rowCount()):
            self.parameterTable.setRowHeight(i, 21)
    
        self.parameterTable.setItem(0,0,QtGui.QTableWidgetItem("A_BlueDetect"))
        self.A_BlueDetectValue = 0
        self.parameterTable.setItem(0,1,QtGui.QTableWidgetItem(str(self.A_BlueDetectValue)))
        self.parameterTable.setItem(1,0,QtGui.QTableWidgetItem("F_BlueDetect"))
        self.F_BlueDetectValue = 0
        self.parameterTable.setItem(1,1,QtGui.QTableWidgetItem(str(self.F_BlueDetectValue)))
        self.parameterTable.setItem(2,0,QtGui.QTableWidgetItem("A_BlueCool"))
        self.A_BlueCoolValue = 0
        self.parameterTable.setItem(2,1,QtGui.QTableWidgetItem(str(self.A_BlueCoolValue)))
        self.parameterTable.setItem(3,0,QtGui.QTableWidgetItem("F_BlueCool"))
        self.F_BlueCoolValue = 0
        self.parameterTable.setItem(3,1,QtGui.QTableWidgetItem(str(self.F_BlueCoolValue)))
        self.parameterTable.setItem(4,0,QtGui.QTableWidgetItem("F_IRon"))
        self.F_IRonValue = 0
        self.parameterTable.setItem(4,1,QtGui.QTableWidgetItem(str(self.F_IRonValue)))
        self.parameterTable.setItem(5,0,QtGui.QTableWidgetItem("F_IROFF"))
        self.F_IROFFValue = 0
        self.parameterTable.setItem(5,1,QtGui.QTableWidgetItem(str(self.F_IROFFValue)))
        self.parameterTable.setItem(6,0,QtGui.QTableWidgetItem("A_IRon"))
        self.A_IRonValue = 0
        self.parameterTable.setItem(6,1,QtGui.QTableWidgetItem(str(self.A_IRonValue)))
        self.parameterTable.setItem(7,0,QtGui.QTableWidgetItem("A_IROFF"))
        self.A_IROFFValue = 0
        self.parameterTable.setItem(7,1,QtGui.QTableWidgetItem(str(self.A_IROFFValue)))
        self.parameterTable.setItem(8,0,QtGui.QTableWidgetItem("F_RedOn"))
        self.F_RedOnValue = 0
        self.parameterTable.setItem(8,1,QtGui.QTableWidgetItem(str(self.F_RedOnValue)))
        self.parameterTable.setItem(9,0,QtGui.QTableWidgetItem("F_RedCenter"))
        self.F_RedCenterValue = 0
        self.parameterTable.setItem(9,1,QtGui.QTableWidgetItem(str(self.F_RedCenterValue)))
        self.parameterTable.setItem(10,0,QtGui.QTableWidgetItem("F_PolarOffset"))
        self.F_PolarOffsetValue = 0
        self.parameterTable.setItem(10,1,QtGui.QTableWidgetItem(str(self.F_PolarOffsetValue)))
        self.parameterTable.setItem(11,0,QtGui.QTableWidgetItem("F_Sec"))
        self.F_SecValue = 0
        self.parameterTable.setItem(11,1,QtGui.QTableWidgetItem(str(self.F_SecValue)))
        self.parameterTable.setItem(12,0,QtGui.QTableWidgetItem("F_Sec2"))
        self.F_Sec2Value = 0
        self.parameterTable.setItem(12,1,QtGui.QTableWidgetItem(str(self.F_Sec2Value)))
        self.parameterTable.setItem(13,0,QtGui.QTableWidgetItem("A_RedOn"))
        self.A_RedOnValue = 0
        self.parameterTable.setItem(13,1,QtGui.QTableWidgetItem(str(self.A_RedOnValue)))
        self.parameterTable.setItem(14,0,QtGui.QTableWidgetItem("A_SCool"))
        self.A_SCoolValue = 0
        self.parameterTable.setItem(14,1,QtGui.QTableWidgetItem(str(self.A_SCoolValue)))
        self.parameterTable.setItem(15,0,QtGui.QTableWidgetItem("A_Polar"))
        self.A_PolarValue = 0
        self.parameterTable.setItem(15,1,QtGui.QTableWidgetItem(str(self.A_PolarValue)))
        self.parameterTable.setItem(16,0,QtGui.QTableWidgetItem("us_MeasTime"))
        self.us_MeasTimeValue = 0
        self.parameterTable.setItem(16,1,QtGui.QTableWidgetItem(str(self.us_MeasTimeValue)))
        self.parameterTable.setItem(17,0,QtGui.QTableWidgetItem("us_RedTime"))
        self.us_RedTimeValue = 0
        self.parameterTable.setItem(17,1,QtGui.QTableWidgetItem(str(self.us_RedTimeValue)))
        self.parameterTable.setItem(18,0,QtGui.QTableWidgetItem("ms_ReadoutDly"))
        self.ms_ReadoutDlyValue = 0
        self.parameterTable.setItem(18,1,QtGui.QTableWidgetItem(str(self.ms_ReadoutDlyValue)))
        self.parameterTable.setItem(19,0,QtGui.QTableWidgetItem("SPloops"))
        self.SPloopsValue = 0
        self.parameterTable.setItem(19,1,QtGui.QTableWidgetItem(str(self.SPloopsValue)))
        self.parameterTable.setItem(20,0,QtGui.QTableWidgetItem("SCloops"))
        self.SCloopsValue = 0
        self.parameterTable.setItem(20,1,QtGui.QTableWidgetItem(str(self.SCloopsValue)))
        self.parameterTable.setItem(21,0,QtGui.QTableWidgetItem("SCloops2"))
        self.SCloops2Value = 0
        self.parameterTable.setItem(21,1,QtGui.QTableWidgetItem(str(self.SCloops2Value)))
        self.parameterTable.setItem(22,0,QtGui.QTableWidgetItem("us_RamseyDly"))
        self.us_RamseyDlyValue = 0
        self.parameterTable.setItem(22,1,QtGui.QTableWidgetItem(str(self.us_RamseyDlyValue)))
        self.parameterTable.setItem(23,0,QtGui.QTableWidgetItem("Ph_Ramsey"))
        self.Ph_RamseyValue = 0
        self.parameterTable.setItem(23,1,QtGui.QTableWidgetItem(str(self.Ph_RamseyValue)))
        self.parameterTable.setItem(24,0,QtGui.QTableWidgetItem("us_PiTime"))
        self.us_PiTimeValue = 0
        self.parameterTable.setItem(24,1,QtGui.QTableWidgetItem(str(self.us_PiTimeValue)))
        self.parameterTable.setItem(25,0,QtGui.QTableWidgetItem("Stupid"))
        self.StupidValue = 0
        self.parameterTable.setItem(25,1,QtGui.QTableWidgetItem(str(self.StupidValue)))
        self.parameterTable.setItem(26,0,QtGui.QTableWidgetItem("SCdiv"))
        self.SCdivValue = 0
        self.parameterTable.setItem(26,1,QtGui.QTableWidgetItem(str(self.SCdivValue)))
        self.parameterTable.setItem(27,0,QtGui.QTableWidgetItem("F_BlueHi"))
        self.F_BlueHiValue = 0
        self.parameterTable.setItem(27,1,QtGui.QTableWidgetItem(str(self.F_BlueHiValue)))
        self.parameterTable.setItem(28,0,QtGui.QTableWidgetItem("F_BlueOn"))
        self.F_BlueOnValue = 0
        self.parameterTable.setItem(28,1,QtGui.QTableWidgetItem(str(self.F_BlueOnValue)))
        self.parameterTable.setItem(29,0,QtGui.QTableWidgetItem("A_BlueOn"))
        self.A_BlueOnValue = 0
        self.parameterTable.setItem(29,1,QtGui.QTableWidgetItem(str(self.A_BlueOnValue)))
        self.parameterTable.setItem(30,0,QtGui.QTableWidgetItem("A_BlueHi"))
        self.A_BlueHiValue = 0
        self.parameterTable.setItem(30,1,QtGui.QTableWidgetItem(str(self.A_BlueHiValue)))
        self.parameterTable.setItem(31,0,QtGui.QTableWidgetItem("Grahame"))
        self.GrahameValue = 0
        self.parameterTable.setItem(31,1,QtGui.QTableWidgetItem(str(self.GrahameValue)))
        self.parameterTable.setItem(32,0,QtGui.QTableWidgetItem("Gurds"))
        self.GurdsValue = 0
        self.parameterTable.setItem(32,1,QtGui.QTableWidgetItem(str(self.GurdsValue)))
        self.parameterTable.setItem(33,0,QtGui.QTableWidgetItem("SPcounter2"))
        self.SPcounter2Value = 0
        self.parameterTable.setItem(33,1,QtGui.QTableWidgetItem(str(self.SPcounter2Value)))

        self.retranslateUi(Form)    
	    
	# Create some extra boxes for future parameters:
        for x in range(34, 40):
            self.parameterTable.setItem(x,0,QtGui.QTableWidgetItem(""))
            self.parameterTable.setItem(x,1,QtGui.QTableWidgetItem(""))
        
        self.retranslateUi(Form)
        # Connect event handlers to functions:
        QtCore.QObject.connect(self.openButton, QtCore.SIGNAL("clicked()"), mainwindow.openFile)
        QtCore.QObject.connect(self.saveAsButton, QtCore.SIGNAL("clicked()"), mainwindow.saveAs)
        QtCore.QObject.connect(self.runButton, QtCore.SIGNAL("clicked()"), mainwindow.pp_run)
        QtCore.QObject.connect(self.stopButton, QtCore.SIGNAL("clicked()"), mainwindow.stop)
        QtCore.QObject.connect(self.readoutButton, QtCore.SIGNAL("clicked()"), mainwindow.readout)
        QtCore.QObject.connect(self.resetPlotButton, QtCore.SIGNAL("clicked()"), mainwindow.resetPlot)
        QtCore.QMetaObject.connectSlotsByName(mainwindow)
    
        ### Create DAQ GUI ###
        self.savePathLabel = QtGui.QLabel("Project Folder:", Form)
        self.savePathLabel.setGeometry(QtCore.QRect(680, 20, 100, 20))
        self.projectSavePathSelect = QtGui.QPushButton("Choose...", Form)
        self.projectSavePathSelect.setGeometry(QtCore.QRect(820, 16, 71, 31))
        QtCore.QObject.connect(self.projectSavePathSelect, QtCore.SIGNAL("clicked()"), mainwindow.chooseProjectDirectory)
        self.savePathLabelPath = QtGui.QLabel(Form)
        self.savePathLabelPath.setGeometry(QtCore.QRect(680, 40, 200, 40))
        self.savePathLabelPath.setText(os.getcwd())
        self.savePathLabelPath.setWordWrap(True)
        self.savePathLabelPath.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        
        self.dataTypeSelectorLabel = QtGui.QLabel("Data from PP to Graph:", Form)
        self.dataTypeSelectorLabel.setGeometry(QtCore.QRect(680, 85, 150, 15))
        self.plotPercentDarkCheckbox = QtGui.QCheckBox("% Dark", Form)
        self.plotPercentDarkCheckbox.setGeometry(QtCore.QRect(680, 100, 70, 15))
        self.plotAverageCheckbox = QtGui.QCheckBox("Average", Form)
        self.plotAverageCheckbox.setGeometry(QtCore.QRect(750, 100, 70, 15))
        
        self.xAxisSelectorLabel = QtGui.QLabel("X-Axis Parameter:", Form)
        self.xAxisSelectorLabel.setGeometry(QtCore.QRect(680, 125, 100, 15))
        self.xAxisSetLabel = QtGui.QLineEdit(Form)
        self.xAxisSetLabel.setGeometry(QtCore.QRect(770, 125, 115, 17))
        
        self.dataTypeSelectorLabel = QtGui.QLabel("Set PP Parameters:", Form)
        self.dataTypeSelectorLabel.setGeometry(QtCore.QRect(680, 152, 150, 15))
        self.openDDSCommandFileButton = QtGui.QPushButton("File...", Form)
        self.openDDSCommandFileButton.setGeometry(QtCore.QRect(820, 145, 71, 31))
        QtCore.QObject.connect(self.openDDSCommandFileButton, QtCore.SIGNAL("clicked()"), mainwindow.chooseDDSFrequencyFile)
        self.rampSettingsBox = QtGui.QTextEdit("# Specify parameters like this<br /># for synchronous execution for<br /># each STEP in order:<br /># SYNC:[NUM STEPS]<br /># [PARAM] = R1 R2 ... Rn<br /># Ri=[NUM STEPS]:[START]:[END] OR [START]:[END] OR [NUM]<br /># ENDSYNC", Form)
        self.rampSettingsBox.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.rampSettingsBox.setStyleSheet("font-size:11pt; font-family:Courier, Courier New")
        self.rampSettingsBox.setGeometry(QtCore.QRect(675, 170, 222, 400))
        
        self.memoryLabel = QtGui.QLabel("PP Memory: -", Form)
        self.memoryLabel.setGeometry(QtCore.QRect(680, 605, 150, 15))
        
        self.startDAQButton = QtGui.QPushButton("Go", Form)
        self.startDAQButton.setGeometry(QtCore.QRect(681, 685, 210, 31))
        QtCore.QObject.connect(self.startDAQButton, QtCore.SIGNAL("clicked()"), mainwindow.startDAQPressed)
        self.stopDAQButton = QtGui.QPushButton("Stop", Form)
        self.stopDAQButton.setGeometry(QtCore.QRect(681, 710, 210, 31))
        QtCore.QObject.connect(self.stopDAQButton, QtCore.SIGNAL("clicked()"), mainwindow.stopDAQPressed)

        # Connect event handlers to functions:
        QtCore.QObject.connect(self.openButton, QtCore.SIGNAL("clicked()"), mainwindow.openFile)
        QtCore.QObject.connect(self.saveAsButton, QtCore.SIGNAL("clicked()"), mainwindow.saveAs)
        QtCore.QObject.connect(self.runButton, QtCore.SIGNAL("clicked()"), mainwindow.pp_run)
        QtCore.QObject.connect(self.stopButton, QtCore.SIGNAL("clicked()"), mainwindow.stop)
        QtCore.QObject.connect(self.readoutButton, QtCore.SIGNAL("clicked()"), mainwindow.readout)
        QtCore.QObject.connect(self.resetPlotButton, QtCore.SIGNAL("clicked()"), mainwindow.resetPlot)
        # Connect clicking "Go" to opening DAQ graph
        QtCore.QObject.connect(self.startDAQButton, QtCore.SIGNAL("clicked()"), mainwindow.DAQreadout)
        QtCore.QMetaObject.connectSlotsByName(mainwindow)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.openButton.setText(QtGui.QApplication.translate("Form", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.saveAsButton.setText(QtGui.QApplication.translate("Form", "Save As", None, QtGui.QApplication.UnicodeUTF8))
        self.runButton.setText(QtGui.QApplication.translate("Form", "Run", None, QtGui.QApplication.UnicodeUTF8))
        self.stopButton.setText(QtGui.QApplication.translate("Form", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.readoutButton.setText(QtGui.QApplication.translate("Form", "Readout", None, QtGui.QApplication.UnicodeUTF8))
        self.resetPlotButton.setText(QtGui.QApplication.translate("Form", "Reset Plot", None, QtGui.QApplication.UnicodeUTF8))
        self.CMDValueLabel.setText(QtGui.QApplication.translate("Form", "-----", None, QtGui.QApplication.UnicodeUTF8))
        self.DATAValueLabel.setText(QtGui.QApplication.translate("Form", "-----", None, QtGui.QApplication.UnicodeUTF8))
        self.WValueLabel.setText(QtGui.QApplication.translate("Form", "-----", None, QtGui.QApplication.UnicodeUTF8))
        self.THRES1Label.setText(QtGui.QApplication.translate("Form", "THRES1", None, QtGui.QApplication.UnicodeUTF8))
        self.THRES0Label.setText(QtGui.QApplication.translate("Form", "THRES0", None, QtGui.QApplication.UnicodeUTF8))
        self.PCValueLabel.setText(QtGui.QApplication.translate("Form", "-----", None, QtGui.QApplication.UnicodeUTF8))
        self.CMDLabel.setText(QtGui.QApplication.translate("Form", "CMD", None, QtGui.QApplication.UnicodeUTF8))
        self.PCLabel.setText(QtGui.QApplication.translate("Form", "PC", None, QtGui.QApplication.UnicodeUTF8))
        self.DATALabel.setText(QtGui.QApplication.translate("Form", "DATA", None, QtGui.QApplication.UnicodeUTF8))
        self.WLabel.setText(QtGui.QApplication.translate("Form", "W", None, QtGui.QApplication.UnicodeUTF8))
        self.DDS0Label.setText(QtGui.QApplication.translate("Form", "DDS0", None, QtGui.QApplication.UnicodeUTF8))
        self.DDS1Label.setText(QtGui.QApplication.translate("Form", "DDS1", None, QtGui.QApplication.UnicodeUTF8))
        self.DDS2Label.setText(QtGui.QApplication.translate("Form", "DDS2", None, QtGui.QApplication.UnicodeUTF8))
        self.DDS3Label.setText(QtGui.QApplication.translate("Form", "DDS3", None, QtGui.QApplication.UnicodeUTF8))
        self.DDS4Label.setText(QtGui.QApplication.translate("Form", "DDS4", None, QtGui.QApplication.UnicodeUTF8))
        self.FrequencyLabel.setText(QtGui.QApplication.translate("Form", "Frequency (MHz)", None, QtGui.QApplication.UnicodeUTF8))
        self.SHUTRLabel.setText(QtGui.QApplication.translate("Form", "SHUTR", None, QtGui.QApplication.UnicodeUTF8))
        self.AmplitudeLabel.setText(QtGui.QApplication.translate("Form", "Amplitude", None, QtGui.QApplication.UnicodeUTF8))
        self.PhaseLabel.setText(QtGui.QApplication.translate("Form", "Phase", None, QtGui.QApplication.UnicodeUTF8))

