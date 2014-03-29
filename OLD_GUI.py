#!/usr/bin/python2.6
# GaTech PP Gui (a modification of MIT PP Gui with collaboration 
#                from Sandia National Labs).
# C. Spencer Nichols
# 5-31-2012
# Craig R. Clark
# 3-23-2012
#------------------------------------------------------------------------------------------------------------------------------------------
# Install Requirments

#WINDOWS

#python2.7  windows  32 bit becuase some of the packages only have 32 bit
# download numpy at http://sourceforge.net/projects/numpy/files/NumPy/1.5.1/ (file--numpy-1.5.1-win32-superpack-python2.7.exe)
# download gtk-all-in-one at http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/ (file--pygtk-all-in-one-2.24.1.win32-py2.7.msi)
# download scipy at http://sourceforge.net/projects/scipy/files/scipy/0.9.0/ (file--scipy-0.9.0-win32-superpack-python2.7.exe)
# download matplotlib at http://sourceforge.net/projects/matplotlib/files/matplotlib/matplotlib-1.1.0/ (file--matplotlib-1.1.0.win32-py2.7.exe)
# need to instal Opal Kelly Software to have appropriate python API

#Other Requirments ---
#Make sure the FPGA id is correct on line 719, 721 and 722.  This can be changed via the Front Panel Softwarw provided by Opal Kelly

#UBUNTU 10.04
# - ubuntu comes with python 2.6 with the following packages:
#     - os, gobject, pango, math, threading, socket, and time
#   - if your version of ubuntu does not have these packages, they must be installed
# - extra packages to install:
#     - numpy and scipy
#         - sudo apt-get install python-numpy python-scipy
#     - gtk2.0
#         - sudo apt-get install python-gtk2
#     - matplotlib
#         - sudo apt-get install python-matplotlib

#UBUNTU 12.04
# - ubuntu comes with python 2.7 with the following packages:
#     - os, gobject, pango, math, threading, socket, and time
#   - if your version of ubuntu does not have these packages, they must be installed
# - to install the extra packages, follow the ubuntu 10.04 instructions

#--------------------------------------------------------------------------------------------------------------------------------------------

import sys
sys.path.append('./include')

import ok, os
import gtk, gobject, pango, math
import numpy
import threading, socket, time
import coltree, etherplug
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from numpy import arange, sin, pi
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.axes import Subplot
from matplotlib.axes import Axes

from ppcomp import *
from adBoard import *
from fpgaInit import *

NETPORT = 11120

#modification from DDScon2 fo xc3s1500 xilinx board on OK XEM 1050-1500
#####################################################################
# class gui
#
# The user interface
#####################################################################
class gui:
    #################################################################
    # DDS Configuration Data
    #
    # user definable DDS properties - ONLY EDIT THESE VARIABLES
    #################################################################
    
    _DDS_name = 'Black_DDS'  #must match FPGA name
    _boards = ('ad9910', 'ad9959')
    
    #only 3 pll circuits in CY22393
    #_FPGA_PLL_baseFrequencies = ()
    #for each output clock : (pll_index, )
    #_FPGA_PLL_outputData = {1: ()}
    
    _FPGA_bitFile = 'DDSfirmware.bit'  #place bitfile in ./FPGA
    _checkOutputs = False
    
    #################################################################
    # __init__
    #
    # Create all the labels, menus, boxes etc.
    #################################################################
    def __init__(self):
        #initialize FPGA
        self.xem = ok.FrontPanel()
        self.xem = fpgaInit(self._DDS_name, 0, self._FPGA_bitFile, 40)
        
        #initialize ADBoards
        self.boards = []
        self.boardChannelIndex = [];
        for i in range(len(self._boards)):
            print 'Initializing board ' + self._boards[i]
            b = adBoard(self.xem, self._boards[i], i)
            b.initialize(self._checkOutputs)
            self.boards.append(b)
            for j in range(b.channelLimit):
                self.boardChannelIndex.append((i, j)) # Append a tuple (board#, channel#)
            
        
        #initialize GUI
        self.lock = threading.Lock()
        self.data = numpy.zeros([100,3], 'Int32')
        self.plotdata = numpy.zeros([100,3], 'Float32')
        self.stateobj = {}
        self.state = {}

        vbox = gtk.VBox(False, 0)
        hbox = gtk.HBox(False, 0)
        window = gtk.Window()
        window.set_title(self._DDS_name + " Controller")

        stateframe = gtk.Frame("State")

        box = self.make_state_view()
        stateframe.add(box)
        progdef = self.make_progdef_view()
        controlbox = self.make_control_view()

        self.figure = plt.figure() # define the Figure
        self.axis1 = self.figure.add_subplot(111)  # Add Plot to the figure
        self.axis2 = self.axis1.twinx() # Add Second plot to figure which uses other yaxis
        self.plot = FigureCanvas(self.figure)  # a gtk.DrawingArea


        # Add frames
        vbox.pack_start(stateframe, False, False, 1)
        vbox.pack_start(self.plot, True, True, 1)
        vbox.pack_start(controlbox, False, False, 1)
        hbox.pack_start(vbox, True, True, 1)
        hbox.pack_start(progdef, False, False, 1)

        window.add(hbox)

        # connect quit signals
        window.connect("delete_event", self.on_quit_activate, None)
        window.connect("destroy", self.on_quit_activate, None)

        # add an idle callback
        #gobject.timeout_add(50, self.update_state) #Changed 50 to 2000 CWC 04042012
        # Done, show it
        window.show_all()


        # start network
        self.plug = etherplug.etherplug(self.service_netcomm, NETPORT)
        for i in range(len(self.boardChannelIndex)):
            self.plug.register_hook('FREQ%i'%i, self.stateobj['DDS%i_FRQ'%i][0].set_value)
            self.plug.register_hook('AMP%i'%i, self.stateobj['DDS%i_AMP'%i][0].set_value)
            
        self.plug.register_hook('SHUTR', self.stateobj['SHUTR'][0].set_value)
        self.plug.register_hook('SETPROG', self.pp_setprog)
        self.plug.register_hook('PARAMETER', self.parameter_set)
        self.plug.register_hook('RUNIT', self.pp_run)
        self.plug.register_hook('NBRIGHT?', self.net_countabove)
        self.plug.register_hook('LASTAVG?', self.net_lastavg)
        self.plug.register_hook('MEMORY?', self.net_memory)
        self.plug.register_hook('PARAMETER?', self.parameter_read)

        return

    def make_state_view(self):
        box = gtk.VBox(False, 0)

        table_aom = gtk.Table(rows=9, columns=4, homogeneous=True)
        table_aom.attach(gtk.Label('Frequency'),1,2,0,1, gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL)
        table_aom.attach(gtk.Label('Amplitude'),2,3,0,1, gtk.FILL, gtk.FILL)
        table_aom.attach(gtk.Label('Phase'),3,4,0,1,gtk.FILL, gtk.FILL)
        s = 0
        for i in range(len(self.boardChannelIndex)):
            table_aom.attach(gtk.Label('DDS%i'%i),0,1,i+1,i+2, gtk.FILL, gtk.FILL)
            # Create a freq spinbutton
            spin, hid = self.make_spin_button(.2, 6, 0, self.boards[self.boardChannelIndex[i][0]].freqLimit, .1, False, 0, self.freq_changed, i)
            self.stateobj['DDS%i_FRQ'%i] = (spin, hid)
            table_aom.attach(spin, 1, 2, i+1, i+2, gtk.FILL, gtk.FILL)
            # Create an amp spinbutton (DDS1)
            spin, hid = self.make_spin_button(.2, 0, 0, self.boards[self.boardChannelIndex[i][0]].ampLimit, 1, False, 0, self.amp_changed, i)
            self.stateobj['DDS%i_AMP'%i] = (spin, hid)
            table_aom.attach(spin, 2, 3, i+1, i+2, gtk.FILL, gtk.FILL)
            # Create a phase spinbutton (DDS1)
            spin, hid = self.make_spin_button(.2, 0, 0, self.boards[self.boardChannelIndex[i][0]].phaseLimit, 100, False, 0, self.phase_changed, i)
            self.stateobj['DDS%i_PHS'%i] = (spin, hid)
            table_aom.attach(spin, 3, 4, i+1, i+2, gtk.FILL, gtk.FILL)
            s = i + 2
        table_aom.attach(gtk.Label('SHUTR'),0,1,s,s+1, gtk.FILL, gtk.FILL)
        table_aom.attach(gtk.Label('THRES0'),0,1,s+1,s+2, gtk.FILL, gtk.FILL)
        table_aom.attach(gtk.Label('THRES1'),2,3,s+1,s+2, gtk.FILL, gtk.FILL)
        spin, hid = self.make_spin_button(.2, 0, 0, 15, 1, False, 0, self.shutter_changed, 0)
        self.stateobj['SHUTR'] = (spin, hid)
        table_aom.attach(spin, 1, 2, s, s+1, gtk.FILL, gtk.FILL)

        spin, hid = self.make_spin_button(.2, 1, 0, 100, 1, False, 0, None, 0)
        self.stateobj['THRES0'] = (spin, hid)
        table_aom.attach(spin, 1, 2, s+1, s+2, gtk.FILL, gtk.FILL)

        spin, hid = self.make_spin_button(.2, 1, 0, 500, 1, False, 100, None, 0)
        self.stateobj['THRES1'] = (spin, hid)
        table_aom.attach(spin, 3, 4, s+1, s+2, gtk.FILL, gtk.FILL)


        table_pp = gtk.Table(rows=2, columns=4, homogeneous=True)
        table_pp.attach(gtk.Label('CMD '),0,1,0,1, gtk.EXPAND|gtk.FILL, gtk.EXPAND|gtk.FILL)
        table_pp.attach(gtk.Label('DATA'),2,3,0,1, gtk.FILL, gtk.FILL)
        table_pp.attach(gtk.Label('PC  '),0,1,1,2, gtk.FILL, gtk.FILL)
        table_pp.attach(gtk.Label('W   '),2,3,1,2, gtk.FILL, gtk.FILL)

        # Create a threshold spinbutton
        self.stateobj['CMD'] = gtk.Label('-----')
        table_pp.attach(self.stateobj['CMD'], 1, 2, 0, 1, gtk.FILL, gtk.FILL)
        self.stateobj['DATA'] = gtk.Label('-----')
        table_pp.attach(self.stateobj['DATA'], 3, 4, 0, 1, gtk.FILL, gtk.FILL)
        self.stateobj['PC'] = gtk.Label('-----')
        table_pp.attach(self.stateobj['PC'], 1, 2, 1, 2, gtk.FILL, gtk.FILL)
        self.stateobj['W'] = gtk.Label('-----')
        table_pp.attach(self.stateobj['W'], 3, 4, 1, 2, gtk.FILL, gtk.FILL)

        box.pack_start(table_aom, True, True, 0)
        box.pack_start(table_pp, True, True, 10)
        return box

    def make_progdef_view(self):
        box = gtk.VBox(False, 0)
        self.params = coltree.typical_ncol_tree([(gobject.TYPE_STRING, 'Parameter Name', 1),
                                                (gobject.TYPE_DOUBLE, 'Parameter Value', 1)])

        keys = coltree.list_keys_from_config('Params:tree')

        for key in keys:
            self.params.add_row(key, 0)
        for i in range(len(keys), 20):
            self.params.add_row('<PARAM%d>'%(i), 0)

        self.params.restore_state('Params')

        box.pack_start(self.params.treeview, True, True, 0)
        return box

    def make_control_view(self):
        box = gtk.HBox(False, 0)

        # buttons to run pulse sequencer
        button_load = gtk.Button("Load", gtk.STOCK_OPEN)
        box.pack_start(button_load, True, True, 0)

        button_save = gtk.Button("Save", gtk.STOCK_SAVE_AS)
        box.pack_start(button_save, True, True, 0)

        button_run = gtk.Button("Run")
        box.pack_start(button_run, True, True, 0)

        button_stop = gtk.Button("Stop")
        box.pack_start(button_stop, True, True, 0)

        button_read = gtk.Button("Readout")
        box.pack_start(button_read, True, True, 0)

        button_plot_reset = gtk.Button("Reset Plot")
        box.pack_start(button_plot_reset, True, True, 0)

        button_run.connect("clicked", self.pp_run)
        button_stop.connect("clicked", self.pp_stop)
        button_load.connect("clicked", self.pp_load)
        button_save.connect("clicked", self.pp_save)
        button_read.connect("clicked", self.pp_readout)
        button_plot_reset.connect("clicked", self.pp_plot_reset)

        return box

    ################################################################
    # on_quit_activate
    #
    # Run when window is closed
    ################################################################
    def on_quit_activate(self, widget, event, data = None):
        self.params.save_state("Params")
        self.plug.close()
        gtk.main_quit()
        return True

    def make_spin_button(self, climb_rate, digits, range_low, range_high, increments, wrap, value, callback, key):
        sb = gtk.SpinButton(None, climb_rate, digits)
        sb.set_range(range_low, range_high)
        sb.set_increments(increments, increments)
        sb.set_wrap(wrap)
        if (value == None):
            value = mcxem.get_state(key)
        sb.set_value(value)
        if callback:
            hid = sb.connect("value-changed", callback, key)
        else:
            hid = None
        return sb, hid

    def service_netcomm(self, f, arg):
        if (self.pp_is_running() and (f != self.pp_run)):
            return "Wait\n"

        gtk.gdk.threads_enter()
        try:
            rv = f(*arg)
        finally:
            gtk.gdk.threads_leave()
        return rv

#    def update_state(self):
#        self.lock.acquire()
#        try:
#			#Commented CWC 04032012
#            data = '\x00'*32
#            self.xem.ReadFromPipeOut(0xA1, data)
#
#            if ((data[:2] != '\xED\xFE') or (data[-2:] != '\xED\x0F')):
#                print "Bad data string: ", map(ord, data)
#                return True
#
#            data = map(ord, data[2:-2])
#
#            #Decode
#            active =  bool(data[1] & 0x80)
#            self.state['pp_PC'] = ((data[1] & 0xF)<<8) + data[0]
#            self.state['pp_W'] = (data[3]<<8) + data[2]
#            self.state['pp_DATA'] = (data[6]<<16) + (data[5]<<8) + data[4]
#            self.state['pp_CMD'] = data[7]
#            for i in range(len(self.boardChannelIndex)):
#                self.state['DDS%i_FRQ'%i] = self.boards(i).freqLimit*((data[11]<<24) + (data[10]<<16) + (data[9]<<8) + data[8])
                #self.state['DDS1_FRQ'] = self.dds_base_freq*((data[15]<<24) + (data[14]<<16) + (data[13]<<8) + data[12])
                #self.state['DDS2_FRQ'] = self.dds_base_freq*((data[19]<<24) + (data[18]<<16) + (data[17]<<8) + data[16])
#            self.state['DDS0_AMP'] = data[20]&0x3F
#            self.state['DDS1_AMP'] = ((data[21]&0xF)<<2) + (data[20]>>6)
#            self.state['DDS2_AMP'] = ((data[22]&0x3)<<4) + (data[21]>>4)
#            self.state['DDS0_PHS'] = (data[23]<<6) + (data[22]>>2)
#            self.state['DDS1_PHS'] = ((data[25]&0x3F)<<8) + (data[24])
#            self.state['DDS2_PHS'] = ((data[27]&0xF)<<10) + (data[26]<<6) + (data[25]>>6)
#            self.state['SHUTR'] = data[27]>>4
#
#            # Display
#            self.stateobj['PC'].set_label('%d'%self.state['pp_PC'])
#            self.stateobj['CMD'].set_label('%d'%self.state['pp_CMD'])
#            self.stateobj['DATA'].set_label('%d'%self.state['pp_DATA'])
#            self.stateobj['W'].set_label('%d'%self.state['pp_W'])
#
#            for key in self.state:
#                if not self.stateobj.has_key(key):
#                    continue
#
#                if ((self.state.has_key('pp_active') and self.state['pp_active']) or active):
#                    self.stateobj[key][0].handler_block(self.stateobj[key][1])
#                    self.stateobj[key][0].set_sensitive(False)
#                    self.stateobj[key][0].set_value(self.state[key])
#                    self.stateobj[key][0].handler_unblock(self.stateobj[key][1])
#                else:
#                    self.stateobj[key][0].set_sensitive(True)
#
#                    if (abs(self.stateobj[key][0].get_value() - self.state[key]) > 1e-6): #modified? 04042012
#                        print "Inconsistent state of %s, actual value:"%(key), self.state[key], self.stateobj[key][0].get_value()
#
#            self.state['pp_active'] =  bool(data[1] & 0x80)
#        finally:
#            self.lock.release()
#
#        return True


    ################################################################
    # Static DDS commands

    def freq_changed(self, widget, data = None):
        freq = widget.get_value()	# frequency in MHz
        board = self.boardChannelIndex[data][0]
        chan = self.boardChannelIndex[data][1]
        #print 'board ' + str(board) + ', channel ' + str(chan)
        self.boards[board].setFrequency(freq, chan, self._checkOutputs)
        return True

    def amp_changed(self, widget, data= None):
        amp = int(max(0, round(widget.get_value())))
        board = self.boardChannelIndex[data][0]
        chan = self.boardChannelIndex[data][1]
        #print 'board ' + str(board) + ', channel ' + str(chan)
        self.boards[board].setAmplitude(amp, chan, self._checkOutputs)
        return True

    def phase_changed(self, widget, data= None):
        phase = int(max(0, round(widget.get_value())))
        board = self.boardChannelIndex[data][0]
        chan = self.boardChannelIndex[data][1]
        #print 'board ' + str(board) + ', channel ' + str(chan)
        self.boards[board].setPhase(phase, chan, self._checkOutputs)
        return True

    def shutter_changed(self, widget, data=None):
        shutter = int(max(0, widget.get_value()))
        self.xem.SetWireInValue(0x00, shutter<<12, 0xF000)    # address, value, mask
        self.xem.UpdateWireIns()
        print "Setting shutter to %d"%(shutter)

        return True


    ################################################################
    # pulse sequencer commands

    def pp_run(self, widget = None, data = None):
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

    def pp_stop(self, widget, data= None):
        self.xem.ActivateTriggerIn(0x40, 3)
        return True

    def pp_save(self, widget, data= None):
        data = self.data
        buttons = (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK)
        d = gtk.FileChooserDialog("Choose File", None, gtk.FILE_CHOOSER_ACTION_SAVE, buttons)
        d.set_current_folder(os.getcwd())

        rv = d.run()
        if rv == gtk.RESPONSE_OK:
            file = d.get_filename()
			#file="Bluetest.pp"
            try:
                fd = open(file, 'w')
                for i in range(len(data)):
                    fd.write('%d %d %d\n'%(data[i, 0], data[i, 1], data[i,2]))
                fd.close
            except Exception, E:
                print E
        d.destroy()

        return True

    def pp_load(self, widget, data = None):
        buttons = (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)
        d = gtk.FileChooserDialog("Choose File", None, gtk.FILE_CHOOSER_ACTION_OPEN, buttons)
        d.set_current_folder(os.getcwd() + '/prog/')

        rv = d.run()
        if rv == gtk.RESPONSE_OK:
            file = d.get_filename()
            print file
            d.destroy()
        else:
            d.destroy()
            return True

        self.pp_setprog(file)

        print file
        self.pp_upload()
        return True

    def pp_setprog(self, file):
        self.codefile = file

        return True

    def pp_upload(self):

        parameters = {}
        for key in self.params.rows:
            parameters.update({key : self.params.get_data(key, 1)})

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
        print "Upload successful in time %fs"%(t2 - t1)
        return True

    def parameter_read(self, name):
        return "RESULT: %g\n"%(self.params.get_data(name, 1))

    def parameter_set(self, name, value):
        self.params.set_data(name, 1, float(value))
        return True

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

    def pp_readout(self, widget = None, data = None):
        self.update_count()

        self.plotdata[:,0:2] = self.data[:,0:2]
        self.plotdata[:,2] = numpy.log(numpy.abs(self.data[:, 2]) + 1)
        self.axis1.clear()
        self.axis2.clear()
        self.axis1.plot(self.plotdata[:,0],self.plotdata[:,1],'r')
        self.axis1.set_ylabel('Counts', color='r')
        self.axis1.set_xlabel('Bins')
        self.axis2.plot(self.plotdata[:,0],self.plotdata[:,2],'b') #should add readout to the plot
        self.axis2.set_ylabel('Hist', color='b')
        self.plot.draw()


        return True

    def pp_reset(self, widget = None, data = None):
        self.xem.ActivateTriggerIn(0x40,0)
        self.xem.ActivateTriggerIn(0x41,0)
        for key in self.stateobj:
            if ((key[:3] != 'DDS') and (key != 'SHUTR')): continue
            self.stateobj[key][0].handler_block(self.stateobj[key][1])
            self.stateobj[key][0].set_value(0.0)
            self.stateobj[key][0].handler_unblock(self.stateobj[key][1])

        return True

    def pp_plot_reset(self, widget = None, data = None):
        self.axis1.clear()  #5h0u1d c134r 7h3 P107
        self.axis2.clear()
        self.plot.draw()
        #reset histogram
        self.data = numpy.zeros([100,3], 'Int32')
        return True


    ###############################################################
    # update_count
    #
    # Displays latest count
    ###############################################################
    def update_count(self):
        t1 = time.time()
        self.xem.SetWireInValue(0x00, 3900, 0x0FFF)	# start addr at 3900
        self.xem.UpdateWireIns()
        self.xem.ActivateTriggerIn(0x41, 1)

        data = '\x00'*400
        self.xem.ReadFromPipeOut(0xA0, data)
        data = map(ord, data)

        for addr in range(100):
            count = (data[4*addr + 3]<<24) + (data[4*addr + 2]<<16) + (data[4*addr + 1]<<8) + data[4*addr]
            #count=numpy.random.normal(25,5,1);
            #count=int(numpy.rint(count))
            self.data[addr][0] = addr
            self.data[addr][1] = count
	        # Histogram
            if (count < 100):
                self.data[count][2] = self.data[count][2] + 1


        t2 = time.time()
        print "Memory read in %.6f seconds" % (t2-t1)
        #print "Memory contents: ", map(hex, map(int, self.data[:,1]))
        return

    def net_countabove(self):
        self.pp_readout()
        count = 0
        threshold0 = self.stateobj['THRES0'][0].get_value()
        threshold1 = self.stateobj['THRES1'][0].get_value()
        for addr in range(100):
            if (self.data[addr][1] > threshold1):
                count = count + 2
            elif (self.data[addr][1] > threshold0):
                count = count + 1

        return "RESULT: %d\n"%(count)

    def net_lastavg(self):
        count = 0
        tot = 0
        threshold0 = self.stateobj['THRES0'][0].get_value()
        threshold1 = self.stateobj['THRES1'][0].get_value()
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




    def net_memory(self):
        self.pp_readout()

        memory = 'RESULT:'
        for addr in range(100):
	    memory = memory + " %i"%(self.data[addr][1])

        return memory + "\n"
        
# gui
app = gui()

# We're threading, init that
gtk.gdk.threads_init()
gtk.gdk.threads_enter()
# Run
try:
    pass
    gtk.main()
finally:
    # If we died, let the child thread know
    print "Quitting..."
gtk.gdk.threads_leave()

