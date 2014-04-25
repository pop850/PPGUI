#!/usr/bin/python2.6
# @author Alex Popescu
# @author Naveena Karusala
# Created 3/11/14

import sys
import os
import datetime

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
        self.ui = Ui_Form()
        
        self.ui.setupUi(self)
        self.setWindowTitle(self._DDS_name + " Pulse Programmer & DAQ")

        # Variable to count the number of runs so far
        self.runNum = 0
        
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

##        # Initialize DAQ graph with zero values
##        self.DAQdata = numpy.zeros([100,3], 'Int32')
##        self.DAQplotdata = numpy.zeros([100,3], 'Float32')
        
        # Initialize DAQ:
        self.DAQ_Running = False
        self.lock = threading.Lock()
        QtCore.QObject.connect(self, QtCore.SIGNAL("updateParamTable(int, PyQt_PyObject)"), self.updateParamTable)
        QtCore.QObject.connect(self, QtCore.SIGNAL("updateDAQGraph(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), self.updateDAQGraph)
    
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
    def pp_run(self, extraParameters=None):
        print "Running PP code..."
        self.xem.ActivateTriggerIn(0x40, 3)
        if extraParameters != None:
            self.pp_upload(extraParameters)
        else:
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
    def pp_upload(self, overrideParams=None):
        print "Uploading .PP code..."
        parameters = {}
        for x in range(0, self.ui.parameterTable.rowCount()):
            param = self.ui.parameterTable.item(x, 0).text().toUtf8().data() # Convert to a normal string from QString
            value = self.ui.parameterTable.item(x, 1).text().toFloat()[0] # Convert value from QString to float
            if len(param) != 0:
                parameters.update({param : value})
        if overrideParams is not None:
            parameters = overrideParams # If parameters are set for override.
        
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
        threshold0 = self.ui.THRES0Box.value()
        threshold1 = self.ui.THRES1Box.value()
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
        threshold0 = self.ui.THRES0Box.value()
        threshold1 = self.ui.THRES1Box.value()
        for addr in range(100):
            if (self.data[addr][1] > threshold1):
                count = count + 2
            elif (self.data[addr][1] > threshold0):
                count = count + 1
        # Net count above threshold 0, below threshold 1?
        return count
    
    
    def closeEvent(self, event):
        print "Saving and quitting..."
        self.save_parameters()

    ################################################################
    # DAQ Functions                                                #
    ################################################################
    
    # The "Go" button was pressed to start the DAQ.
    def startDAQPressed(self):
        if self.DAQ_Running:
            print "DAQ already running!"
            return
        self.DAQ_Running = True
        print "Starting DAQ run"
        self.DAQ_STOP = False
        if self.lock.locked():
            self.lock.release() # Release any held locks
        
        # Interpret the ramp values:
        ramp_values = self.interpretramp_values()
        if len(ramp_values) == 0:
            print "No values to ramp, aborting DAQ run!"
            return
        
        # Find x-axis:
        xparam_name = self.ui.xAxisSetLabel.text().toUtf8().data()
        print ramp_values.keys()
        print xparam_name
        if xparam_name not in ramp_values.keys():
            print "X parameter: '%s' not valid! Capitalization matters!" % xparam_name
            return False
        
        # CREATE GRAPH:
        DAQ_PWin = pg.plot(title = "Percent Dark vs. %s"%xparam_name, pen = 'r') # Create new plot window
        DAQ_PWin.setLabel('left', "Percent Dark", units='%')
        DAQ_PWin.setLabel('bottom', xparam_name)
        DAQ_PWin.showGrid(x=False, y=True)
        DAQ_PWin_graph = DAQ_PWin.getPlotItem()
        
        # Execute on a background thread to not hold up GUI:
        experiment_thread = threading.Thread(target=self.runDAQExperiment, args=(ramp_values, DAQ_PWin_graph, xparam_name))
        experiment_thread.start()
        
    
    def runDAQExperiment(self, ramp_values, daq_graph, xparam_name):
        # Get x-axis values:
        xparam_vals = ramp_values[xparam_name]
        
        self.lock.acquire()
        # Get current parameter values from interface:
        parameters = {}
        rowNums = {}
        self.DAQ_Params = parameters
        for x in range(0, self.ui.parameterTable.rowCount()):
            param = self.ui.parameterTable.item(x, 0).text().toUtf8().data() # Convert to a normal string from QString
            value = self.ui.parameterTable.item(x, 1).text().toFloat()[0] # Convert value from QString to float
            if len(param) != 0:
                parameters[param] = value
                rowNums[param] = x
        self.lock.release()
        print "Starting run of %i samples for %i parameter(s)" % (len(xparam_vals), len(ramp_values))
        
        listDark = []
        for s in range(0, len(xparam_vals)):
            # Modify parameters that were changed in the DAQ ramp code:
            for p in ramp_values:
                if s < len(ramp_values[p]):
                    parameters[p] = ramp_values[p][s] # Use the value for this parameter at this timestep
                else:
                    parameters[p] = ramp_values[p][-1] # If no value is defined, use last defined value.
                self.lock.acquire()
                try:
                    # Update GUI:
                    self.emit(QtCore.SIGNAL("updateParamTable(int, PyQt_PyObject)"), rowNums[p], str(parameters[p]))
                finally:
                    self.lock.release()
    
            # All parameters are set, run PP experiments:
            self.lock.acquire()
            try:
                print "Run PP Experiment"
                self.pp_run(parameters)
                netCountAbove = self.net_countabove()
                percentDark = 100 - netCountAbove
                listDark.append(percentDark)

                # Plot data:
                self.xValues = xparam_vals[0:s+1]
                self.yValues = listDark
                self.emit(QtCore.SIGNAL("updateDAQGraph(PyQt_PyObject, PyQt_PyObject, PyQt_PyObject)"), daq_graph, xparam_vals[0:s+1], listDark[:])
            except:
                print "Error running PP experiment!"
            finally:
                self.lock.release()
            
            time.sleep(1/20.0) # Let GUI Update
            
            #Check if stopped:
            if self.DAQ_STOP is True:
                self.DAQ_Running = False
                # Automatically saves DAQ data/graph file if run is STOPPED
                self.DAQsaveAs(daq_graph)
                return                
            
            
        # Done.
        self.DAQ_Running = False
        self.DAQsaveAs(daq_graph)

    
    def updateParamTable(self, rowNum, val_str):
        self.lock.acquire()
        try:
            self.ui.parameterTable.item(rowNum, 1).setText(val_str)
            self.ui.parameterTable.update()
        finally:
            self.lock.release()
        return
    
    def updateDAQGraph(self, DAQGraph, newxdata, newydata):
        self.lock.acquire()
        try:
            DAQGraph.plot(newxdata, newydata, pen=(255,0,255), clear=True)            
            DAQGraph.update()
        finally:
            self.lock.release()
        return
    
    
    def stopDAQPressed(self):
        self.DAQ_STOP = True
        self.DAQ_Running = False
        print "DAQ Stopped"


    # This method saves the DAQ Graph to a file in the cwd
    # using the date, time, and run number
    def DAQsaveAs(self, plotItem):
        self.runNum += 1
        
        print("Saving DAQ graph and data...")
        
        dateString = datetime.datetime.now().strftime("%m-%d-%y-%a-%I %M%p-")
        fileString = datetime.datetime.now().strftime("%m-%d-%y-%a")

        dirPath = os.path.join(os.getcwd(), fileString)
        fDataName = dateString + "Run " + str(self.runNum) + ".txt"

        if not os.path.exists(dirPath):
            os.makedirs(dirPath)        
            
        try:
            fd = open(os.path.join(dirPath, fDataName), "wb")
            for i in range(len(self.xValues)):
                fd.write('%f, %f\n'%(self.xValues[i], self.yValues[i]))
            fd.close
        except Exception, E:
            print E

        fGraphName = dateString + "Graph " + str(self.runNum) + ".jpg"
        exporter = pg.exporters.ImageExporter.ImageExporter(plotItem)
        exporter.parameters()['width'] = 500
        exporter.export(os.path.join(dirPath, fGraphName))
        
        return True
    
    # Create a matrix of the different parameters that are changing, and what their value
    # will be at each "PP-run" sample step.
    def interpretramp_values(self):
        text = self.ui.rampSettingsBox.toPlainText().toUtf8().data()
        textlines = text.split("\n")
        usedParams = [] # Parameters that have been parsed so far.
        paramsOfTime = {} # Parameters as a function of time
        sync = False # Whether SYNC is enabled.
        startSyncTime = 0 # Timestep ON which a synch starts (timesteps start from 0)
        currentSyncLength = 0 # The length of the current sync-box
        
        for line in textlines:
            # Check for comments:
            validLine = line
            if len(line.split("#")) > 1:
                validLine = line.split("#")[0] # Only the part before the "#" is valid.
            if len(validLine) == 0:
                continue # This is an empty line.
            
            # Check for SYNC commands:
            if len(validLine.split(":")) == 2:
                sp = validLine.split(":")
                if sp[0].strip() == "SYNC":
                    if sync is True:
                        print "Error: SYNC is already on!: %s" % line
                        continue
                    sync = True # Turn on sync
                    
                    try:
                        currentSyncLength = int(sp[1].strip())
                    except:
                        e = sys.exc_info()[0]
                        print "Error %s interpreting SYNC steps, skipping: %s" % (e, line)
                    continue
            if validLine.strip() == "ENDSYNC":
                if sync is False:
                    print "Error: SYNC is already off!: %s" % line
                    continue
                sync = False # Turn off sync
                startSyncTime = startSyncTime + currentSyncLength # Increment by length of last block
                continue
            
            # Parse equality assignment:
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
            
            # Ensure that we are in a SYNC block, since we are assigning values:
            if sync is not True:
                print "Line is not in a SYNC block, skipping!:\n%s\n" % line
                continue
            
            # Now that param is validated, attempt to find its values:
            actualVals = []
            for rg in vals:
                srg = rg.split(":")
                v = None
                
                try:
                    if len(srg) == 1:
                        # This is simply a number
                        v = [ float(srg[0].strip()) ]
                    elif len(srg) == 2:
                        # A range, in increments of 1
                        v = numpy.arange(float(srg[0].strip()), float(srg[1].strip())).tolist()
                        v.append(float(srg[1].strip()))
                    elif len(srg) == 3:
                            # Create a range with a STEP:
                            v = numpy.linspace(float(srg[1].strip()), float(srg[2].strip()), num=float(srg[0].strip())).tolist()
                    else:
                        print "Error evaluating '%s' in line:\n%s\n" % (rg, line)
                        continue
                    actualVals.extend(v)
                except:
                    e = sys.exc_info()[0]
                    print "Error %s parsing line:\n%s\n" % (e, line)
                    continue
            # Ensure we are adding the right length:
            if len(actualVals) != currentSyncLength:
                print "Number of steps in SYNC-block (%i) not equal to steps in line:\n%s\n" % (currentSyncLength, line)
                continue
            
            # Use for debugging:
            print param
            print actualVals
            
            # Add a new entry in the parameters as a function of time, if necessary
            if param not in usedParams:
                paramsOfTime[param] = []
                usedParams.append(param)
            
            # Fill with last value, if necessary.
            if len(paramsOfTime[param]) < startSyncTime:
                paramsOfTime[param].extend( [paramsOfTime[param][-1]] * (startSyncTime - len(paramsOfTime[param])) )
                print "Warning: %s filled %i values!" % (param, startSyncTime - len(paramsOfTime[param]))
            paramsOfTime[param].extend( actualVals )
        
        # Use for debugging:
        print "Parameters as a function of DAQ run:"
        for param in paramsOfTime:
            print param, paramsOfTime[param]
        
        return paramsOfTime
    

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    app.setActiveWindow(MainWindow)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
