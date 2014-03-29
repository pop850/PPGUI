# FAKE_ok.py
# This is a FAKE implementation of the _ok.so library, which communicates with hardware
# in the experiment.
# These are some sort of clock source reference, set to something to not break other code:
PLL22150_ClkSrc_Ref = 1
PLL22150_ClkSrc_Div1ByN = 1
PLL22150_ClkSrc_Div1By2 = 1
PLL22150_ClkSrc_Div1By3 = 1
PLL22150_ClkSrc_Div2ByN = 1
PLL22150_ClkSrc_Div2By2 = 1
PLL22150_ClkSrc_Div2By4 = 1
PLL22150_DivSrc_Ref = 1
PLL22150_DivSrc_VCO = 1
PLL22393_ClkSrc_Ref = 1
PLL22393_ClkSrc_PLL0_0 = 1
PLL22393_ClkSrc_PLL0_180 = 1
PLL22393_ClkSrc_PLL1_0 = 1
PLL22393_ClkSrc_PLL1_180 = 1
PLL22393_ClkSrc_PLL2_0 = 1
PLL22393_ClkSrc_PLL2_180 = 1



def ConfigureFPGA(self, *args):
    return
def delete_PLL22150(self, *args):
    # Called when SWIG deletes the PLL22150
    return

def PLL22150_swigregister(self, *args):
    return
def delete_PLL22393(self, *args):
    return
def PLL22393_swigregister(self, *args):
    return
    
# Frontpanel functions & constants:
FrontPanel_brdUnknown = 1
FrontPanel_brdXEM3001v1 = 1
FrontPanel_brdXEM3001v2 = 1
FrontPanel_brdXEM3010 = 1
FrontPanel_brdXEM3005 = 1
FrontPanel_brdXEM3001CL = 1
FrontPanel_brdXEM3020 = 1
FrontPanel_brdXEM3050 = 1
FrontPanel_brdXEM9002 = 1
FrontPanel_brdXEM3001RB = 1
FrontPanel_brdXEM5010 = 1
FrontPanel_brdXEM6110LX45 = 1
FrontPanel_brdXEM6110LX150 = 1
FrontPanel_brdXEM6001 = 1
FrontPanel_brdXEM6010LX45 = 1
FrontPanel_brdXEM6010LX150 = 1
FrontPanel_NoError = 1
FrontPanel_Failed = 1
FrontPanel_Timeout = 1
FrontPanel_DoneNotHigh = 1
FrontPanel_TransferError = 1
FrontPanel_CommunicationError = 1
FrontPanel_InvalidBitstream = 1
FrontPanel_FileError = 1
FrontPanel_DeviceNotOpen = 1
FrontPanel_InvalidEndpoint = 1
FrontPanel_InvalidBlockSize = 1
FrontPanel_I2CRestrictedAddress = 1
FrontPanel_I2CBitError = 1
FrontPanel_I2CNack = 1
FrontPanel_I2CUnknownStatus = 1
FrontPanel_UnsupportedFeature = 1
FrontPanel_FIFOUnderflow = 1
FrontPanel_FIFOOverflow = 1
FrontPanel_DataAlignmentError = 1

readout_value_1 = 0 # What to read out from a wire

def delete_FrontPanel(self, *args): return
def new_FrontPanel(): return

def FrontPanel_ActivateTriggerIn(self, *args):
    return
def FrontPanel_ConfigureFPGA(self, *args):
    return
def FrontPanel_EnableAsynchronousTransfers(self, *args):
    return
def FrontPanel_GetBoardModel(self):
    return
def FrontPanel_GetBoardModelString(self, *args):
    return "This is a Fake Board"
def FrontPanel_GetDeviceCount(self):
    return 2
def FrontPanel_GetDeviceID(self):
    return "Black_DDS"
def FrontPanel_GetDeviceListModel(self, *args):
    return
def FrontPanel_GetDeviceListSerial(self, *args):
    return 1012345
def FrontPanel_GetDeviceMajorVersion(self):
    return 1.0
def FrontPanel_GetDeviceMinorVersion(self):
    return 1.0
def FrontPanel_GetEepromPLL22150Configuration(self, *args):
    return 1
def FrontPanel_GetEepromPLL22393Configuration(self, *args):
    return 1
def FrontPanel_GetPLL22150Configuration(self, *args):
    return 1
def FrontPanel_GetPLL22393Configuration(self, *args):
    return 1
def FrontPanel_GetSerialNumber(self):
    return 101011010
def FrontPanel_GetWireOutValue(self, wire):
    global readout_value_1
    if wire == 0x24:
        return readout_value_1
    return 1
def FrontPanel_GetHostInterfaceWidth(self):
    return 500
def FrontPanel_IsHighSpeed(self):
    return True
def FrontPanel_IsFrontPanel3Supported(self):
    return True
def FrontPanel_IsFrontPanelEnabled(self):
    return True
def FrontPanel_IsOpen(self):
    return True
def FrontPanel_IsTriggered(self, *args):
    return False
def FrontPanel_LoadDefaultPLLConfiguration(self):
    return
def FrontPanel_OpenBySerial(self, *args):
    return 0
def FrontPanel_ResetFPGA(self):
    return
def FrontPanel_SetBTPipePollingInterval(self, *args):
    return 0
def FrontPanel_SetDeviceID(self, *args):
    return
def FrontPanel_SetEepromPLL22150Configuration(self, *args):
    return
def FrontPanel_SetEepromPLL22393Configuration(self, *args):
    return
def FrontPanel_SetPLL22150Configuration(self, *args):
    return
def FrontPanel_SetPLL22393Configuration(self, *args):
    return
def FrontPanel_SetTimeout(self, *args):
    return
def FrontPanel_SetWireInValue(self, address, value, mask = None): #Mask isn't necessary
    # Tell the wire out what to read, to trick the adBoard.py board-import script.
    global readout_value_1
    if address == 0x00:
        if value == 0<<2:
            readout_value_1 = 2
        elif value == 1<<2:
            readout_value_1 = 1
    return
def FrontPanel_UpdateTriggerOuts(self):
    return
def FrontPanel_UpdateWireIns(self):
    return
def FrontPanel_UpdateWireOuts(self):
    return
def FrontPanel_WriteToPipeIn(self, *args):
    return
def FrontPanel_ReadFromPipeOut(self, *args):
    return 
def FrontPanel_WriteToBlockPipeIn(self, *args):
    return 
def FrontPanel_ReadFromBlockPipeOut(self, *args):
    return
def FrontPanel_WriteToPipeInThr(self, *args):
    return
def FrontPanel_ReadFromPipeOutThr(self, *args):
    return
def FrontPanel_WriteToBlockPipeInThr(self, *args):
    return
def FrontPanel_ReadFromBlockPipeOutThr(self, *args):
    return
def FrontPanel_ReadI2C(self, *args):
    return True
def FrontPanel_WriteI2C(self, *args):
    return True
def FrontPanel_swigregister(self, *args):
    return True