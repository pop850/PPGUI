###########################################################################
#
#   ShelvingSPSC allows for spin polarization loops and sideband cooling loops using the silver DDS 
#   Brown Lab, 2012
#   Adapted from Skeleton.pp Jan 17 2008
#   Does the same stuff as Shelving.pp, written for the ppcomp_jan2008.py compiler.
#
#   Expects the following parameters to be defined:
#       F_BlueDetect, A_BlueDetect, F_IRon
#
#       included BasicReadout.pp expects the following parameters to be defined:
#           us_MeasTime, us_RedTime, ms_ReadoutDly, F_IRon, F_RedOn, A_RedOn, F_BlueCool, A_BlueCool
#       included Init_StateS0.pp expects the following parameters to be defined:
#           F_IRon, F_BlueCool, A_BlueCool, SCloops, F_RedCenter, F_RedPL, A_RedPL, F_Sec, A_SCool
#
# All parameters are automatically added as registers that are globally
# accessible by included ("inserted") files.
# May 26 2009 - changed IRDelay from NS to US scale -KRB
# Remember that the DDS channels are being defined, they aren't commented out

# a define gives aliases for numbers

#define REDDDS	   1 
#define BLUEDDS	   0
#define IRDDS	   2


var datastart 3900
var dataend 4000
var addr 0
var sample 0
# constants:
var F_OFF          0
var A_OFF          0   
var F_BOFF         0
var A_BOFF         0   
var US_CHECKTIME   250 # changed from 200 to 10000 Craig April 7 2011 - measurement time to see if the ion is in the ground state after 854 repumping 
var CHECKTHOLD     3 # should be above Thres0*uschecktime/measuretime - checks that the ion is cold and that the 854 worked
var US_POLARTIME   7 # pi time for the peak we are polarizing with
var POLARDIV       100 # No longer used in this code; kept for now
var US_SCTIMEINIT  9 # initial pi time of the red sideband
var NS_SCINC       50 # linear extrapolation from init red pi time to final RPT.  (init-final)/scloops
var US_IRDELAY     10 # how long 854 is on to deshelve during polarization and sideband cooling.  Optimize by slowly scaling back and checking deshelving
var US_DOPPLERCOOL 500 # how long to leave the lower power blue on to Doppler cool
var F_RedPL        (F_RedCenter + F_PolarOffset)
var F_RedSC        (F_RedCenter + F_Sec)
var F_RedRed       (F_RedCenter + F_RedOn)
# manipulated variables:
var us_sctime      0
var SPcounter      0
var SCcounter      0
var Divcounter     0

	LDWR     datastart # load datastart to the working register
	STWR     addr      # store the working register in variable addr (these two lines set the address to the start position)
# label(optional) function variables
# initialize
init: DDSFRQ   IRDDS, F_IRon    
    SHUTR    0 # turn the 854 amplitude on
	DDSFRQ   BLUEDDS, F_BlueDetect #turn the blue laser on and check for an ion
    DDSAMP	 BLUEDDS, A_BlueDetect   
	COUNT	 US_CHECKTIME	# put photon counts into W register
	CMP      CHECKTHOLD 	# if counts greater than threshold W=W else W=0
	JMPZ     init  		# if W=0 back to init

    DDSFRQ   IRDDS, F_IROFF 	# turns the 854 frequency off so we can run the experiment.  Turning off as soon as we can in case
    SHUTR    2 		            # turns the 854 amplitude off 
    DDSFRQ	 BLUEDDS, F_BlueCool  # Doppler cool at the lower power
	DDSAMP	 BLUEDDS, A_BlueCool
	DELAY    US_DOPPLERCOOL    
	DDSAMP   BLUEDDS, A_BOFF
	DDSFRQ	 BLUEDDS, F_BOFF

	LDWR     SPloops       # Polarization Loops
	JMPZ	 done          # if SPloops=0 it skips to done
	STWR     SPcounter       # put SPloops into counter  
	
    LDWR	 SCloops
	STWR	 SCcounter
	
    LDWR     US_SCTIMEINIT
	STWR     us_sctime
	

polar: NOP                       
	DDSFRQ	 REDDDS, F_RedPL
	DDSAMP	 REDDDS, A_Polar
	DELAY    US_POLARTIME
	DDSAMP	 REDDDS, A_OFF	
	DDSFRQ	 REDDDS, F_OFF
	DDSFRQ   IRDDS, F_IRon
    SHUTR    0 		            # turns the 854 amplitude on
	DELAY	 US_IRDELAY
	DDSFRQ   IRDDS, F_IROFF
    SHUTR    2 		            # turns the 854 amplitude off
	DEC      SPcounter
	STWR     SPcounter
	JMPNZ    polar

    LDWR     SCdiv
    STWR     Divcounter

    LDWR     SCcounter
    JMPZ     done

scool: NOP 
	DDSFRQ	 REDDDS, F_RedSC
	DDSAMP	 REDDDS, A_SCool
	DELAY    us_sctime
	DDSAMP	 REDDDS, A_OFF
	DDSFRQ	 REDDDS, F_OFF
	DDSFRQ   IRDDS, F_IRon
    SHUTR    0 		            # turns the 854 amplitude on
	DELAY	 US_IRDELAY
	DDSFRQ   IRDDS, F_IROFF
    SHUTR    2 		            # turns the 854 amplitude off

	LDWR     us_sctime
	ADDW     NS_SCINC
	STWR     us_sctime
    DEC      Divcounter
	DEC      SCcounter
	STWR     SCcounter
	JMPZ     done
    STWR     Divcounter
    JMPZ     polar
	JMPNZ    scool           

polar2: NOP                       
	DDSFRQ	 REDDDS, F_RedPL
	DDSAMP	 REDDDS, A_Polar
	DELAY    US_POLARTIME
	DDSAMP	 REDDDS, A_OFF	
	DDSFRQ	 REDDDS, F_OFF
	DDSFRQ   IRDDS, F_IRon
    SHUTR    0 		            # turns the 854 amplitude on
	DELAY	 US_IRDELAY
	DDSFRQ   IRDDS, F_IROFF
    SHUTR    2 		            # turns the 854 amplitude off
	DEC      SPcounter2
	STWR     SPcounter2
	JMPNZ    polar2

    LDWR     SCdiv
    STWR     Divcounter

    LDWR     SCcounter
    JMPZ     done              

done: NOP # finish initialization

# measure

	DELAY    ms_ReadoutDly

	DDSFRQ	 REDDDS, F_RedRed # F_RedRed is the Red center plus an offset defined in the daq for pumping on additional sidebands
	DDSAMP	 REDDDS, A_RedOn

	DELAY    us_RedTime

	DDSAMP	 REDDDS, A_OFF
	DDSFRQ	 REDDDS, F_OFF 
	
    DDSFRQ	 BLUEDDS, F_BlueDetect
	DDSAMP	 BLUEDDS, A_BlueDetect

	COUNT    us_MeasTime


	STWR     sample         #stores data from readout into W register

	LDINDF   addr
	LDWR     sample
	STWI                
	INC      addr    # W= addr+1
 	STWR     addr   # addr=W
	CMP      dataend # if addr less than dataend W=0 
	JMPZ     init  #if W=0 continue (have not reached the end of the address)
	DDSFRQ   IRDDS, F_IRon
    SHUTR    0
	DDSFRQ	 BLUEDDS, F_BlueCool
	DDSAMP	 BLUEDDS, A_BlueCool
	END
