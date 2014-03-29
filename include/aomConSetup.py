#!/usr/bin/python2.4

import ok
import time

xem = ok.FrontPanel()
module_count = xem.GetDeviceCount()

print "Found %d modules"%(module_count)
if (module_count == 0): raise "No XEMs found!"

for i in range(module_count):
	serial = xem.GetDeviceListSerial(i)

xem.OpenBySerial(serial)



print "Loading PLL config"
pll = ok.PLL22393()
xem.GetEepromPLL22393Configuration(pll)
#pll.SetVCOParameters(1, 48)
xem.SetPLL22393Configuration(pll)
pll.GetOutputFrequency(0)

print "Programming FPGA"
xem.ConfigureFPGA('aomController.bit')

time.sleep(.1)
print "Setting PLL multiplication"

xem.SetWireInValue(0x04,0xE0)
xem.UpdateWireIns()
xem.UpdateWireOuts()
xem.GetWireOutValue(0x25)

xem.ActivateTriggerIn(0x41,0)

#PLL multiplication ratio 24 bits w/ 2-level modulation
xem.SetWireInValue(0x01,0x0501)
xem.SetWireInValue(0x02,0x9400)
xem.SetWireInValue(0x03,0x0000)
xem.UpdateWireIns()
xem.UpdateWireOuts()
xem.GetWireOutValue(0x20)
xem.GetWireOutValue(0x21)
xem.GetWireOutValue(0x22)
xem.GetWireOutValue(0x23)
xem.GetWireOutValue(0x24)
xem.ActivateTriggerIn(0x40,0)

time.sleep(.1)
print "Setting 110MHz tuning word"

#frequency tuning word 32 bits
xem.SetWireInValue(0x00,0x0040)
xem.SetWireInValue(0x01,0x0604)

#200 MHZ
#xem.SetWireInValue(0x02,0x6666)
#xem.SetWireInValue(0x03,0x6666)

#110 MHZ
xem.SetWireInValue(0x02,0x3851)
xem.SetWireInValue(0x03,0xEB85)

#80 MHZ
#xem.SetWireInValue(0x02,0x28F5)
#xem.SetWireInValue(0x03,0xC28F)

xem.UpdateWireIns()
xem.UpdateWireOuts()
xem.GetWireOutValue(0x20)
xem.GetWireOutValue(0x21)
xem.GetWireOutValue(0x22)
xem.GetWireOutValue(0x23)
xem.GetWireOutValue(0x24)
xem.ActivateTriggerIn(0x40,0)

time.sleep(.1)
print "Setting amplitude"

#amplitude tuning word 24 bits
xem.SetWireInValue(0x01,0x0506)
xem.SetWireInValue(0x02,0x0013)   #0013
xem.SetWireInValue(0x03,0xFFFF)   #FFFF full power #0000 half power
xem.UpdateWireIns()
xem.UpdateWireOuts()
xem.GetWireOutValue(0x20)
xem.GetWireOutValue(0x21)
xem.GetWireOutValue(0x22)
xem.GetWireOutValue(0x23)
xem.GetWireOutValue(0x24)
xem.ActivateTriggerIn(0x40,0)

time.sleep(.1)
print "Setting amplitude modulation"

#Frequency, Phase, or Amplitude modulation selection
xem.SetWireInValue(0x01,0x0503)
xem.SetWireInValue(0x02,0x4003)
xem.SetWireInValue(0x03,0x0000)
xem.UpdateWireIns()
xem.UpdateWireOuts()
xem.GetWireOutValue(0x20)
xem.GetWireOutValue(0x21)
xem.GetWireOutValue(0x22)
xem.GetWireOutValue(0x23)
xem.GetWireOutValue(0x24)
xem.ActivateTriggerIn(0x40,0)

time.sleep(.1)
print "Setting off profile map"

#second amplitude for profile map
xem.SetWireInValue(0x01,0x050A)
xem.SetWireInValue(0x02,0x0000)
xem.SetWireInValue(0x03,0x0000)
xem.UpdateWireIns()
xem.UpdateWireOuts()
xem.GetWireOutValue(0x20)
xem.GetWireOutValue(0x21)
xem.GetWireOutValue(0x22)
xem.GetWireOutValue(0x23)
xem.GetWireOutValue(0x24)
xem.ActivateTriggerIn(0x40,0)

print "ALL DONE!!!!"
