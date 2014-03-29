#!/usr/bin/python2.6
# @author Alex Popescu
# @author Naveena Karusala
# Created 3/11/14
# NOTE: Only one PP GUI can be open at a time!

import sys
import os

# Packages used: PyQt, PyQtGraph, Scipy

from PyQt4 import QtCore, QtGui
from New_GUI_ui import Ui_Form

# From include folder
sys.path.append('./include')
import ok
import numpy
from numpy import arange, sin, pi
import threading, socket, time
import etherplug

from ppcomp import *
from adBoard import *
from fpgaInit import *

import pyqtgraph as pg
__name__
NETPORT = 11120
CONFIG_FILE = "BlackPulseProgrammerConfig.ddscon"

class MyForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        # Configurable DDS properties:
        self._DDS_name = 'Black_DDS'  # Must match FPGA name
        self._boards = ('ad9910', 'ad9959')
        self._FPGA_bitFile = 'DDSfirmware.bit'  # Place bitfile in ./FPGA
        self._checkOutputs = False
        
        # Initialize FPGA
        self.xem = ok.FrontPanel()
        self.xem = fpgaInit(self._DDS_name, 0, self._FPGA_bitFile, 40)
        
        # Initialize ADBoards
        # The DDSs on these boards will be put in the "DDS" list, in the order of the boards,
        # then in the order of the channel for the DDS on each board.
        self.boards = []
        self.boardChannelIndex = [];
        for i in range(len(self._boards)):
            print 'Initializing board ' + self._boards[i]
            b = adBoard(self.xem, self._boards[i], i)
            b.initialize(self._checkOutputs)
            self.boards.append(b)
            for j in range(b.channelLimit):
                self.boardChannelIndex.append((i, j))
                print "DDS %i = Board %i, Channel %i" % (i+j, i, j)
                    
        # Initialize UI window
        self.lock = threading.Lock()
        self.ui = Ui_Form()
        
        self.ui.setupUi(self)
        self.setWindowTitle(self._DDS_name + " Pulse Programmer & DAQ")
        
        # Update limits for the input FREQ, AMP, PHASE boxes
        for i in range(len(self.boardChannelIndex)):
            self.ui.stateobj['DDS%i_FREQ'%i].setRange(0, self.boards[self.boardChannelIndex[i][0]].freqLimit)
            self.ui.stateobj['DDS%i_AMP'%i].setRange(0, self.boards[self.boardChannelIndex[i][0]].ampLimit)
            self.ui.stateobj['DDS%i_PHASE'%i].setRange(0, self.boards[self.boardChannelIndex[i][0]].phaseLimit)
        
        # Load parameters from previous usage of this app
        self.load_parameters()
        
        # Initialize graph with zero values
        self.data = numpy.zeros([100,3], 'Int32')
        self.plotdata = numpy.zeros([100,3], 'Float32')
        self.ui.histogram_dataitem = None
            
        # Start network
        self.plug = etherplug.etherplug(self.service_netcomm, NETPORT)
        for i in range(len(self.boardChannelIndex)):
            self.plug.register_hook('FREQ%i'%i, self.ui.stateobj['DDS%i_FREQ'%i].setValue)
            self.plug.register_hook('AMP%i'%i, self.ui.stateobj['DDS%i_AMP'%i].setValue)
            
        self.plug.register_hook('SHUTR', self.ui.stateobj['SHUTR'].setValue)
        self.plug.register_hook('SETPROG', self.pp_setprog)
        self.plug.register_hook('PARAMETER', self.parameter_set)
        self.plug.register_hook('RUNIT', self.pp_run)
        self.plug.register_hook('NBRIGHT?', self.net_countabove)
        self.plug.register_hook('LASTAVG?', self.net_lastavg)
        self.plug.register_hook('MEMORY?', self.net_memory)
        self.plug.register_hook('PARAMETER?', self.parameter_read)
        

    # This method opens a dialog that allows the user to select a .PP file from the
    # filesystem. The .PP is then sent to the Pulse Programmer to be stored in RAM.
    def openFile(self):
        # Open PP file        
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open PP File', 
                os.getcwd() + '/prog/')
        fname = fname.toUtf8().data() # Convert QString to normal string
        
        try:
            f = open(fname, 'r')
        except IOError:
            print 'Error opening PP file ', fname
            return False
        else:
            print fname
            f.close()
            self.codefile = fname
            # Send the .PP file to the Pulse Programmer
            return self.pp_upload()
    
    # This method saves the data obtained from the Pulse Programmer to a selected data
    # file.
    def saveAs(self):
        data = self.data
        fname = QtGui.QFileDialog.getSaveFileName(self, 'Save Data File', 
                os.getcwd())
        
        try:
            fd = open(fname, 'w')
            for i in range(len(data)):
                fd.write('%d %d %d\n'%(data[i, 0], data[i, 1], data[i,2]))
            fd.close
        except Exception, E:
            print E
        
        return True
    
        
    def resetPlot(self):
        # Reset graph:
        self.data = numpy.zeros([100,3], 'Int32')
        self.ui.counts_graph.clear()
        if self.ui.histogram_dataitem != None: #Try to remove the last histogram data object
            self.ui.histogram_graph.removeItem(self.ui.histogram_dataitem)
            self.ui.histogram_dataitem = None
    
    
    ################################################################
    # Static DDS commands                                          #
    ################################################################
    def freq_changed(self, value):
    	print "Changed frequency for DDS %i to %f" % (self.sender().dds_num, value)
    	freq = value	# frequency in MHz
    	dds = self.sender().dds_num # Refers to physical DDS chip, though these can be grouped on the same board.
        board = self.boardChannelIndex[dds][0]
        chan = self.boardChannelIndex[dds][1]
        #print 'board ' + str(board) + ', channel ' + str(chan)
        self.boards[board].setFrequency(freq, chan, self._checkOutputs)
        return True
    	
    def amp_changed(self, value):
    	print "Changed amplitude for DDS %i to %d" % (self.sender().dds_num, value)
    	amp = int(max(0, value))
    	dds = self.sender().dds_num # Refers to physical DDS chip, though these can be grouped on the same board.
        board = self.boardChannelIndex[dds][0]
        chan = self.boardChannelIndex[dds][1]
        #print 'board ' + str(board) + ', channel ' + str(chan)
        self.boards[board].setAmplitude(amp, chan, self._checkOutputs)
        return True
    	
    def phase_changed(self, value):
    	print "Changed phase for DDS %i to %d" % (self.sender().dds_num, value)
    	phase = int(max(0, value))
    	dds = self.sender().dds_num # Refers to physical DDS chip, though these can be grouped on the same board.
        board = self.boardChannelIndex[dds][0]
        chan = self.boardChannelIndex[dds][1]
        #print 'board ' + str(board) + ', channel ' + str(chan)
        self.boards[board].setPhase(phase, chan, self._checkOutputs)
        return True
    
    def shutter_changed(self, value):
    	print "Changed shutter to %d" % value
    	shutter = int(max(0, value))
        self.xem.SetWireInValue(0x00, shutter<<12, 0xF000)    # address, value, mask
        self.xem.UpdateWireIns()
        return True
    
    ################################################################
    # Pulse Sequencer Commands                                     #
    ################################################################
    # This method runs the .PP file that has been loaded into the Pulse Programmer.
    def pp_run(self):
        DDS0FrequencyValue = self.ui.DDS0FrequencyBox.value()
        DDS1FrequencyValue = self.ui.DDS1FrequencyBox.value()
        DDS2FrequencyValue = self.ui.DDS2FrequencyBox.value()
        DDS3FrequencyValue = self.ui.DDS3FrequencyBox.value()
        DDS4FrequencyValue = self.ui.DDS4FrequencyBox.value()
        DDS0AmplitudeValue = self.ui.DDS0AmplitudeBox.value()
        DDS1AmplitudeValue = self.ui.DDS1AmplitudeBox.value()
        DDS2AmplitudeValue = self.ui.DDS2AmplitudeBox.value()
        DDS3AmplitudeValue = self.ui.DDS3AmplitudeBox.value()
        DDS4AmplitudeValue = self.ui.DDS4AmplitudeBox.value()
        DDS0PhaseValue = self.ui.DDS0PhaseBox.value()
        DDS1PhaseValue = self.ui.DDS1PhaseBox.value()
        DDS2PhaseValue = self.ui.DDS2PhaseBox.value()
        DDS3PhaseValue = self.ui.DDS3PhaseBox.value()
        DDS4PhaseValue = self.ui.DDS4PhaseBox.value()
        SHUTRValue = self.ui.SHUTRBox.value()
        THRES0Value = self.ui.THRES0Box.value()
        THRES1Value = self.ui.THRES1Box.value()
        #insert code to calculate and plot the graph
        
        print "Running PP code..."
        self.xem.ActivateTriggerIn(0x40, 3)
        self.pp_upload()
        self.xem.ActivateTriggerIn(0x40, 2)

        time.sleep(0.2)

        if (self._checkOutputs):
            print 'shifting out'
            self.xem.SetWireInValue(0x00, (1<<2)) 
            self.xem.UpdateWireIns()
            self.xem.UpdateWireOuts()
            print hex(self.xem.GetWireOutValue(0x20))
            print hex(self.xem.GetWireOutValue(0x21))
            print hex(self.xem.GetWireOutValue(0x22))
            print hex(self.xem.GetWireOutValue(0x23))
            #print 'test_o'
            #print hex(self.xem.GetWireOutValue(0x25))
        return True
    
    # This method loads the specified .PP file (that was selected in OpenFile()) into the
    # Pulse Programmer. The .PP file specifies a series of commands to execute once the
    # trigger is activated.
    def pp_upload(self):
        print "Uploading .PP code..."
        parameters = {}
        for x in range(0, self.ui.parameterTable.rowCount()):
            param = self.ui.parameterTable.item(x, 0).text().toUtf8().data() # Convert to a normal string from QString
            value = self.ui.parameterTable.item(x, 1).text().toFloat()[0] # Convert value from QString to float
            parameters.update({param : value})
        
        code = pp2bytecode(self.codefile, self.boardChannelIndex, self.boards, parameters)

        databuf = ''
        for op, arg in code:
            memword = '%c%c'%((arg&0xFF), (arg>>8)&0xFF) + '%c%c'%((arg>>16)&0xFF, op + (arg>>24))
            print '%x, %x, %x, %x' %(ord(memword[0]), ord(memword[1]), ord(memword[2]), ord(memword[3]))
            databuf = databuf + memword

        t1 = time.time()
        self.xem.SetWireInValue(0x00, 0, 0x0FFF)	# start addr at zero
        self.xem.UpdateWireIns()
        self.xem.ActivateTriggerIn(0x41, 1)
        self.xem.WriteToPipeIn(0x80, databuf)
        t2 = time.time()
        print "Upload successful in time %fs for file \'%s\'"%(t2 - t1, os.path.relpath(self.codefile))
        return True
        
    def stop(self):
        self.xem.ActivateTriggerIn(0x40, 3)
        print "Stop signal sent."
        return

    # This method reads data back from the Pulse Programmer, and then draws a plot of the data.
    def readout(self):
        self.update_count()

        self.plotdata[:,0:2] = self.data[:,0:2]
        self.plotdata[:,2] = numpy.log(numpy.abs(self.data[:, 2]) + 1)
        
        self.ui.counts_graph.clear()
        # Plot counts vs experiment done:
        self.ui.counts_graph.plot(self.plotdata[:,0], self.plotdata[:,1], pen=(255,0,0))
        # Plot count histogram:
        children = self.ui.histogram_graph.allChildren() # Remove all current data in histogram graph.
        
        if self.ui.histogram_dataitem != None: #Try to remove the last histogram data
            self.ui.histogram_graph.removeItem(self.ui.histogram_dataitem)
            self.ui.histogram_dataitem = None
        
        hist_data = pg.PlotDataItem(self.plotdata[:,0],self.plotdata[:,2], pen=(0,0,255))
        self.ui.histogram_graph.addItem( hist_data )
        self.ui.histogram_dataitem = hist_data
        return
    
    # This method does the actual reading of data from the Pulse Programmer.
    def update_count(self):
        t1 = time.time()
        self.xem.SetWireInValue(0x00, 3900, 0x0FFF)	# start addr at 3900
        self.xem.UpdateWireIns()
        self.xem.ActivateTriggerIn(0x41, 1)

        data = '\x00'*400 # Pre-populate data list with NULL characters.
        self.xem.ReadFromPipeOut(0xA0, data) # Store read data from wire 0xA0 in data
        data = map(ord, data) # Turn every character of data into an integer corresponding to the Unicode code point of the character.

        for addr in range(100):
            count = (data[4*addr + 3]<<24) + (data[4*addr + 2]<<16) + (data[4*addr + 1]<<8) + data[4*addr]
            # COMMENT THESE NEXT TWO LINES!!!: (FOR OFF-LINE TESTING ONLY)
            count=numpy.random.normal(25,5,1)
            count=int(numpy.rint(count))
            self.data[addr][0] = addr
            self.data[addr][1] = count
	        # Histogram
            if (count < 100):
                self.data[count][2] = self.data[count][2] + 1


        t2 = time.time()
        print "Memory read in %.6f seconds" % (t2-t1)
        #print "Memory contents: ", map(hex, map(int, self.data[:,1]))
        return
        
    def pp_is_running(self):
        self.lock.acquire()
        try:
			#Commented CWC 04032012
            data = '\x00'*32
            self.xem.ReadFromPipeOut(0xA1, data)

            if ((data[:2] != '\xED\xFE') or (data[-2:] != '\xED\x0F')):
                print "Bad data string: ", map(ord, data)
                return True

            data = map(ord, data[2:-2])

            #Decode
            active =  bool(data[1] & 0x80)
        finally:
            self.lock.release()

        return active
    
    def pp_setprog(self, file):
        self.codefile = file

        return True
    
    ################################################################
    # Parameter Functionality                                      #
    ################################################################
    def load_parameters(self):
        print "Loading saved parameters..."
        self.params = QtCore.QSettings(CONFIG_FILE, QtCore.QSettings.NativeFormat) # Create settings object.
        num_params = self.ui.parameterTable.rowCount()
        for x in range(0, num_params):
            param = self.ui.parameterTable.item(x, 0)
            value = self.params.value(param.text(), None)
            if value == None:
                value = "0"
            else:
                value = value.toString()
            
            self.ui.parameterTable.item(x, 1).setText(value)
    
    # Runs when the window is closed:
    def save_parameters(self):
        num_params = self.ui.parameterTable.rowCount()
        for x in range(0, num_params):
            param = self.ui.parameterTable.item(x, 0)
            value = self.ui.parameterTable.item(x, 1)
            self.params.setValue(param.text(), value.text())
    
    def parameter_set(self, name, value):
        self.params.setValue(name, value)
        return True
    
    def parameter_read(self, name):
        return "RESULT: %s\n"%(self.params.value(name).toFloat()[0])
    
    ################################################################
    # Network Functionality                                        #
    ################################################################
    def service_netcomm(self, f, arg):
        if (self.pp_is_running() and (f != self.pp_run)):
            return "Wait\n"

        try:
            rv = f(*arg)
        finally:
            print ""
        return rv
    
    def net_memory(self):
        self.readout()

        memory = 'RESULT:'
        for addr in range(100):
	    memory = memory + " %i"%(self.data[addr][1])

        return memory + "\n"
    
    def net_lastavg(self):
        count = 0
        tot = 0
        threshold0 = self.ui.stateobj['THRES0'].value()
        threshold1 = self.ui.stateobj['THRES1'].value()
        for addr in range(100):
            if (self.data[addr][1] > threshold1):
                count = count + 2
                tot = tot + self.data[addr][1]
            elif (self.data[addr][1] >= threshold0):  #changed this line to >= from >  For heating rate exp.  (Craig Oct 24 2008)
                count = count + 1
                tot = tot + self.data[addr][1]
        
        if (count < 5):
       	    return "RESULT: 0\n"
        else:
            return "RESULT: %f\n"%(1.0*tot/count)
    
    def net_countabove(self):
        self.readout()
        count = 0
        threshold0 = self.ui.stateobj['THRES0'].value()
        threshold1 = self.ui.stateobj['THRES1'].value()
        for addr in range(100):
            if (self.data[addr][1] > threshold1):
                count = count + 2
            elif (self.data[addr][1] > threshold0):
                count = count + 1

        return "RESULT: %d\n"%(count)
    
    
    def closeEvent(self, event):
        print "Saving and quitting..."
        self.save_parameters()
        self.plug.close() # Close network connections.

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    app.setActiveWindow(MainWindow)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
