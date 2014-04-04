#!/usr/bin/python2.6
# @author Alex Popescu
# @author Naveena Karusala
# Created 3/11/14

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
        
        self.projectSavePath = os.getcwd()
        
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
    
    # Choose a new project directory to save all files from experiments:
    def chooseProjectDirectory(self):
        fname = QtGui.QFileDialog.getExistingDirectory(self, 'Choose Project Folder', 
                os.getcwd())
        fname = fname.toUtf8().data() # Convert QString to normal string
        if len(fname) == 0:
            return # The dialog was cancelled!
        self.projectSavePath = fname
        self.ui.savePathLabelPath.setText(fname)
        print 'Set project directory to ', fname
    
    # Choose file with AOM frequencies to run, instead of typing them in.
    def chooseDDSFrequencyFile(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Choose PP Parameter File', 
                os.getcwd())
        fname = fname.toUtf8().data() # Convert QString to normal string
        try:
            f = open(fname, 'r')
        except IOError:
            print 'Error opening PP parameter file ', fname
            return False
        else:
            print fname
            self.ui.rampSettingsBox.setText( f.read() )
            f.close()
    
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
    
    
    ################################################################
    # Static DDS commands                                          #
    ################################################################
    def freq_changed(self, value):
        print "Changed frequency for DDS %i to %f" % (self.sender().dds_num, value)
        freq = value    # frequency in MHz
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
        self.xem.SetWireInValue(0x00, 0, 0x0FFF)    # start addr at zero
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
        max_counts = numpy.amax(self.plotdata[:,1])
        max_hist = numpy.amax(self.plotdata[:,2])
        
        self.ui.counts_graph.plot(self.plotdata[:,0],numpy.multiply(self.plotdata[:,2], max_counts/max_hist), pen=(0,0,255))
        return
    
    # This method does the actual reading of data from the Pulse Programmer.
    def update_count(self):
        t1 = time.time()
        self.xem.SetWireInValue(0x00, 3900, 0x0FFF)    # start addr at 3900
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
            param = self.ui.parameterTable.item(x, 0).text()
            if param.isEmpty():
                continue # Skip unused params
            value = self.params.value(param.toUtf8().data(), None)
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
            if param.text().isEmpty(): #Skip this parameter if it is empty.
                continue
            self.params.setValue(param.text().toUtf8().data(), value.text().toUtf8().data())
    
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
    
    # The "Go" button was pressed to start the DAQ.
    def startDAQPressed(self):
        #Interpret the ramp values:
        rampValues = self.interpretRampValues()
    
    def stopDAQPressed(self):
        print "hi"
    
    # Create a matrix of the different parameters that are changing, and what their value
    # will be at each "PP-run" sample step.
    def interpretRampValues(self):
        text = self.ui.rampSettingsBox.toPlainText().toUtf8().data()
        textlines = text.split("\n")
        synch = False
        usedParams = []
        
        for line in textlines:
            validLine = line
            if len(line.split("#")) > 1:
                validLine = line.split("#")[0] # Only the part before the "#" is valid.
            if len(validLine) == 0:
                continue # This is an empty line.
            if validLine.strip() == "SYNCH":
                synch = True # Turn on synch
            elif validLine.strip() == "ENDSYNCH":
                synch = False # Turn off synch
            
            ops = validLine.split("=")
            if len(ops) != 2:
                print "Error parsing line, incorrect use of '=':\n%s\n" % line
                continue
            
            param = ops[0].split()[0] # The parameter to vary
            vals = ops[1].split()  # What values to set parameter to
            
            # Check this parameter is valid:
            validParam = False
            for x in range(0, self.ui.parameterTable.rowCount()):
                ep = self.ui.parameterTable.item(x, 0).text().toUtf8().data()
                if ep == param:
                    validParam = True
                    break
            if validParam == False:
                print "Parameter '%s' not found in line:\n%s\n" % (param, line)
                continue
            
            # Make sure this param is noted as varying:
            if param not in usedParams:
                usedParams.append(param)
            
            # Now that param is validated, attempt to find ranges:
            actualVals = []
            for rg in vals:
                srg = rg.split(":")
                v = None
                if len(srg) == 1:
                    # This is simply a number
                    v = [ float(srg[0].strip()) ]
                elif len(srg) == 2:
                    # A range, in increments of 1
                    v = numpy.arange(float(srg[0].strip()), float(srg[1].strip())).tolist()
                    v.append(float(srg[1].strip()))
                elif len(srg) == 3:
                    if float(srg[0].strip()) == float(srg[2].strip()):
                        # Simply repeat the same value a certain number of times:
                        v = [float(srg[0].strip())] * int(srg[1].strip())
                    else:
                        # Create a range with a STEP:
                        v = numpy.arange(float(srg[0].strip()), float(srg[2].strip()), float(srg[1].strip())).tolist()
                        v.append(float(srg[2].strip()))
                else:
                    print "Error evaluating '%s' in line:\n%s\n" % (rg, line)
                actualVals.extend(v)
            print param
            print actualVals
            
            
            
        print usedParams
            

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    app.setActiveWindow(MainWindow)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
