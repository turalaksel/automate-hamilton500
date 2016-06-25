#!/usr/bin/env python

import time
import serial

def is_number(s):
    '''
    Checks whether a string is numeric or not
    '''
    try:
        float(s)
        return True
    except ValueError:
        return False

def parse_command(command):
    '''
    Parse the command written
    '''
    command_list = command.split()
    function = command_list[0]
    params   = []
    if len(command_list) > 1:
        params   = command_list[1:]
    return function,params

def check_left_syringe(params=[]):
    '''
    Checks the syringe position
    '''
    command = 'aBYQP\r\n'
    SER.write(command)
    literal,ascii = read_port()
    position = int(''.join(literal[8:-1]))
    return position

def check_right_syringe(params=[]):
    '''
    Checks the syringe position
    '''
    command = 'aCYQP\r\n'
    SER.write(command)
    literal,ascii = read_port()
    position = int(''.join(literal[8:-1]))
    return position
    
def read_port(params=[]):
    '''
    Returns literals and ascii codes of the read bytes
    '''
    literal = []
    # let's wait one second before reading output (let's give device time to answer)
    time.sleep(1)
    while SER.inWaiting() > 0:
            literal.append(SER.read(1))
    ascii = [ord(x) for x in literal]
    return literal,ascii
    
def home_syringes(params=[]):
    '''
    Home the syringes for fresh start
    '''
    command = 'aXR\r\n'
    SER.write(command)
    literal,ascii = read_port()

def initialize(params=[]):
    '''
    Initialize the sytem
    '''
    #Get address(a) for the titrator 
    command = '1a\r\n'
    SER.write(command)
    literal,ascii = read_port()
    
    #Set the speed
    command = 'aBYSS005CYSS005R\r\n'
    SER.write(command)
    literal,ascii = read_port()
    #Home the syringes
    home_syringes()
    
    #Set the resolution
    set_resolution()
    
def set_resolution(params=[]):
    '''
    Sets the resolution of the syringe steps
    '''
    command = 'aBYSM'+str(RESOLUTION)+'CYSM'+str(RESOLUTION)+'R\r\n'
    SER.write(command)
    literal,ascii = read_port()
    
def fill_disp_left_syringe(params=[2500]):
    '''
    VOLUME in microliters
    '''
    volume = float(params[0])
    if volume > LEFT_SYRINGE:
        print 'Volume for Left Syringe fill is not valid. Pick a smaller value than '+str(LEFT_SYRINGE)
        return
    num_steps = int(FULL_STEPS*volume/LEFT_SYRINGE)
    command = 'aBIM'+str(num_steps)+'>T100R\r\n'
    SER.write(command)
    literal,ascii = read_port()
    position = 0
    while position != num_steps:
        position = check_left_syringe()
    command = 'aBOM0>T100R\r\n'
    SER.write(command)
    literal,ascii = read_port()
    while position != 0:
        position = check_left_syringe()
    actual_volume = 1.0*LEFT_SYRINGE*num_steps/FULL_STEPS
    return actual_volume

def fill_disp_right_syringe(params=[2500]):
    '''
    VOLUME in microliters
    '''
    volume =float(params[0])
    if volume > RIGHT_SYRINGE:
        print 'ERROR:Volume for Left Syringe fill is not valid. Pick a smaller value than '+str(LEFT_SYRINGE)
        return
    num_steps = int(FULL_STEPS*volume/RIGHT_SYRINGE)
    command = 'aCIM'+str(num_steps)+'>T100R\r\n'
    SER.write(command)
    literal,ascii = read_port()
    position = 0
    while position != num_steps:
        position = check_right_syringe()
    command = 'aCOM0>T100R\r\n'
    SER.write(command)
    literal,ascii = read_port()
    while position != 0:
        position = check_right_syringe()
    actual_volume = 1.0*RIGHT_SYRINGE*num_steps/FULL_STEPS
    return actual_volume

def fill_disp_both_syringes_simulate(params=[2500,2500]):
    volume_left  = float(params[0])
    volume_right = float(params[1])
    
    if volume_left > LEFT_SYRINGE or volume_right > RIGHT_SYRINGE:
        print 'ERROR:Check your volumes'
        return
    
    num_steps_left  = int(FULL_STEPS*volume_left/LEFT_SYRINGE)
    num_steps_right = int(FULL_STEPS*volume_right/RIGHT_SYRINGE)
    
    actual_volume_left  = 1.0*LEFT_SYRINGE*num_steps_left/FULL_STEPS
    actual_volume_right = 1.0*RIGHT_SYRINGE*num_steps_right/FULL_STEPS
    
    return actual_volume_left, actual_volume_right


def fill_disp_both_syringes(params=[2500,2500]):
    volume_left  = float(params[0])
    volume_right = float(params[1])
    
    if volume_left > LEFT_SYRINGE or volume_right > RIGHT_SYRINGE:
        print 'ERROR:Check your volumes'
        return
    
    num_steps_left  = int(FULL_STEPS*volume_left/LEFT_SYRINGE)
    num_steps_right = int(FULL_STEPS*volume_right/RIGHT_SYRINGE)
    
    command = 'aBIM'+str(num_steps_left)+'CIM'+str(num_steps_right)+'>T100R\r\n'
    SER.write(command)
    literal,ascii = read_port()
    
    #Wait until the syringes go to their destination
    position = 0
    while position != num_steps_left:
        position = check_left_syringe()
    
    position = 0
    while position != num_steps_right:
        position = check_right_syringe()
        
    command = 'aBOM0COM0>T100R\r\n'
    SER.write(command)
    literal,ascii = read_port()
    
    #Wait until the syringes go to 0
    position = num_steps_left
    while position != 0:
        position = check_left_syringe()
    
    position = num_steps_right
    while position != 0:
        position = check_right_syringe()
    
    actual_volume_left  = 1.0*LEFT_SYRINGE*num_steps_left/FULL_STEPS
    actual_volume_right = 1.0*RIGHT_SYRINGE*num_steps_right/FULL_STEPS
    
    return actual_volume_left, actual_volume_right

def fill_disp_both_oversize_simulate(params=[2500.0,2500.0]):
    '''
    Fills both syringes but at least one volume exceeds the syringe size
    '''
    left_vol   = float(params[0])
    right_vol  = float(params[1]) 
    left_steps = int(left_vol/LEFT_SYRINGE)
    left_extra = left_vol - left_steps*LEFT_SYRINGE
    
    right_steps = int(right_vol/RIGHT_SYRINGE)
    right_extra = right_vol - right_steps*RIGHT_SYRINGE
    
    left_extra_actual,right_extra_actual = fill_disp_both_syringes_simulate([left_extra,right_extra])
    left_actual  = left_steps*LEFT_SYRINGE+left_extra_actual
    right_actual = right_steps*RIGHT_SYRINGE+right_extra_actual
    actual_conc  = (left_actual*LEFT_SOLUTION + right_actual*RIGHT_SOLUTION)/(left_actual+right_actual)
    
    return left_actual,right_actual,actual_conc

def fill_disp_both_oversize(params=[2500.0,2500.0]):
    '''
    Fills both syringes but at least one volume exceeds the syringe size
    '''
    left_vol   = float(params[0])
    right_vol  = float(params[1]) 
    left_steps = int(left_vol/LEFT_SYRINGE)
    left_extra = left_vol - left_steps*LEFT_SYRINGE
    
    right_steps = int(right_vol/RIGHT_SYRINGE)
    right_extra = right_vol - right_steps*RIGHT_SYRINGE
    
    #Determine the minimum steps(right or left)
    min_steps  = right_steps
    left_min   = False
    if left_steps < min_steps:
        min_steps = left_steps
        left_min  = True
    
    #Do the common fills together
    for i in range(min_steps):
        fill_disp_both_syringes([LEFT_SYRINGE,RIGHT_SYRINGE])
    
    if left_min:
        for i in range(min_steps,right_steps):
            fill_disp_both_syringes([0.0,RIGHT_SYRINGE])
    else:
        for i in range(min_steps,left_steps):
            fill_disp_both_syringes([LEFT_SYRINGE,0.0])
            
    #Do the extra fills
    left_extra_actual,right_extra_actual = fill_disp_both_syringes([left_extra,right_extra])
    left_actual  = left_steps*LEFT_SYRINGE+left_extra_actual
    right_actual = right_steps*RIGHT_SYRINGE+right_extra_actual
    actual_conc  = (left_actual*LEFT_SOLUTION + right_actual*RIGHT_SOLUTION)/(left_actual+right_actual)
    
    return left_actual,right_actual,actual_conc

def prime_syringes(params=[2]):
    '''
    Prime the syringes 5 times
    '''
    steps = int(params[0])
    for i in range(steps):
        command = 'aBIM'+str(FULL_STEPS)+'CIM'+str(FULL_STEPS)+'>T100R\r\n'
        SER.write(command)
        literal,ascii = read_port()
        position = 0
        while position != FULL_STEPS:
            position = check_right_syringe()
        command = 'aBOM0COM0>T100R\r\n'
        SER.write(command)
        literal,ascii = read_port()
        while position != 0:
            position = check_right_syringe()

def prep_sf_solutions(params=[]):
    '''
    Prepare solutions for SF experiments
    '''
    first_point = 1.0*UNFOLDED_SOLUTION/DILUTION
    final_point = 1.0*RIGHT_SOLUTION*DILUTION/(DILUTION+1)
    #Modified on 11/08/11
    if MAX_DENATURANT < final_point:
        final_point = MAX_DENATURANT
    
    ref_log_book = 'ref_solutions.dat'
    unf_log_book = 'unf_solutions.dat'
    
    ref = open(ref_log_book,'w')
    unf = open(unf_log_book,'w')
    
    total_left_solution  = 0.0
    total_right_solution = 0.0
    
    ref.write('%-8s\t%-8s\t%-8s\t%-8s\t%-8s\n'%('Number','Total(uL)','Left(uL)','Right(uL)','[Den]'))
    unf.write('%-8s\t%-8s\t%-8s\t%-8s\t%-8s\n'%('Number','Total(uL)','Left(uL)','Right(uL)','[Den]'))
    
    print 'Preparing refolding solutions'
    input = raw_input("Are you ready for refolding solutions?")
    #First prepare refolding solutions
    num_ref_points  = int((RIGHT_POINT - first_point)/SPACING_REF) + 1
    for i in range(num_ref_points):
        input = raw_input("Refolding solution "+str(i+1))
        target_conc  = first_point + i*SPACING_REF
        diluent_conc = ((DILUTION+1.0)*target_conc - UNFOLDED_SOLUTION)/DILUTION
        left_vol   = SF_DILUENT_VOL*(diluent_conc - RIGHT_SOLUTION)/(LEFT_SOLUTION - RIGHT_SOLUTION)
        right_vol  = SF_DILUENT_VOL - left_vol
        total_left_solution  +=left_vol
        total_right_solution +=right_vol
        left_actual,right_actual,actual_conc = fill_disp_both_oversize([left_vol,right_vol])
        actual_vol = left_actual+right_actual
        print "Total:%.3f\tLeft:%.3f\tRight:%.3f\tConc:%.3f"%(actual_vol,left_actual,right_actual,actual_conc)
        ref.write("%d\t%.3f\t%.3f\t%.3f\t%.3f\n"%(i+1,actual_vol,left_actual,right_actual,actual_conc))
    
    print 'Preparing unfolding solutions'
    input = raw_input("Are you ready for unfolding solutions?")
    #Now prepare unfolding solutions
    num_unf_points  = int((final_point - LEFT_POINT)/SPACING_UNF) + 1
    for i in range(num_unf_points):
        input = raw_input("Unfolding solution "+str(i+1))
        target_conc = LEFT_POINT + i*SPACING_UNF
        diluent_conc = ((DILUTION+1.0)*target_conc - FOLDED_SOLUTION)/DILUTION
        left_vol   = SF_DILUENT_VOL*(diluent_conc - RIGHT_SOLUTION)/(LEFT_SOLUTION - RIGHT_SOLUTION)
        right_vol  = SF_DILUENT_VOL - left_vol
        total_left_solution  +=left_vol
        total_right_solution +=right_vol
        
        left_actual,right_actual,actual_conc = fill_disp_both_oversize([left_vol,right_vol])
        print "Total:%.3f\tLeft:%.3f\tRight:%.3f\tConc:%.3f"%(actual_vol,left_actual,right_actual,actual_conc)
        unf.write("%d\t%.3f\t%.3f\t%.3f\t%.3f\n"%(i+1,actual_vol,left_actual,right_actual,actual_conc))
    
    print 'Preparing FOLDED sample'
    input = raw_input("Are you ready for FOLDED sample?")
    #Now prepare folded solution
    left_vol  =  ((SF_SAMPLE_VOL-PROTEIN_VOL)*(FOLDED_SOLUTION - RIGHT_SOLUTION)+(FOLDED_SOLUTION*PROTEIN_VOL))/(LEFT_SOLUTION - RIGHT_SOLUTION)
    right_vol =  SF_SAMPLE_VOL - PROTEIN_VOL - left_vol
    left_actual,right_actual,actual_conc = fill_disp_both_oversize([left_vol,right_vol])
    actual_vol = left_actual+right_actual
    total_left_solution  +=left_vol
    total_right_solution +=right_vol
    print "Left:%.3f\tRight:%.3f\tConc:%.3f\t Protein Vol:%.3f"%(left_actual,right_actual,actual_conc,PROTEIN_VOL)
    unf.write("\nFOLDED SAMPLE\tTOTAL:%.3f\tLEFT:%.3f\tRIGHT:%.3f\tCONC:%.3f\tADD PROTEIN(uL)\t%.3f\n"%(actual_vol,left_actual,right_actual,actual_conc,PROTEIN_VOL))
    print "TOTAL FOLDED SAMPLE VOLUME %.3f\t FINAL CONC: %.3f"%(actual_vol+PROTEIN_VOL,actual_conc*actual_vol/(actual_vol+PROTEIN_VOL))
    
    print 'Preparing UNFOLDED sample'
    input = raw_input("Are you ready for UNFOLDED sample?")
    #Now prepare unfolded solution
    left_vol  =  ((SF_SAMPLE_VOL-PROTEIN_VOL)*(UNFOLDED_SOLUTION - RIGHT_SOLUTION)+(UNFOLDED_SOLUTION*PROTEIN_VOL))/(LEFT_SOLUTION - RIGHT_SOLUTION)
    right_vol =  SF_SAMPLE_VOL - PROTEIN_VOL - left_vol
    left_actual,right_actual,actual_conc = fill_disp_both_oversize([left_vol,right_vol])
    actual_vol = left_actual+right_actual
    total_left_solution  +=left_vol
    total_right_solution +=right_vol
    print "Left:%.3f\tRight:%.3f\tConc:%.3f\t Protein Vol:%.3f"%(left_actual,right_actual,actual_conc,PROTEIN_VOL)
    ref.write("\nUNFOLDED SAMPLE\tTOTAL:%.3f\tLEFT:%.3f\tRIGHT:%.3f\tCONC:%.3f\tADD PROTEIN(uL)\t%.3f\n"%(actual_vol,left_actual,right_actual,actual_conc,PROTEIN_VOL))
    print "TOTAL UNFOLDED SAMPLE VOLUME %.3f\t FINAL CONC: %.3f"%(actual_vol+PROTEIN_VOL,actual_conc*actual_vol/(actual_vol+PROTEIN_VOL))
    print "TOTAL REFOLDING SOLUTIONS:%3d\tTOTAL UNFOLDING SOLUTIONS:%3d"%(num_ref_points,num_unf_points)
    print "TOTAL LEFT(uL):%.3f\tTOTAL RIGHT(uL):%.3f\tTOTAL UNFOLDED PROTEIN(uL):%.3f\t TOTAL FOLDED PROTEIN(uL):%.3f"%(total_left_solution,total_right_solution,400*num_ref_points,400*num_unf_points)
    
    ref.close()
    unf.close()

def prep_sf_solutions_simulate(params=[]):
    '''
    Prepare solutions for SF experiments
    '''
    first_point = 1.0*UNFOLDED_SOLUTION/DILUTION
    final_point = 1.0*RIGHT_SOLUTION*DILUTION/(DILUTION+1)
    #Modified on 11/08/11
    if MAX_DENATURANT < final_point:
        final_point = MAX_DENATURANT
    
    ref_log_book = 'ref_solutions.dat'
    unf_log_book = 'unf_solutions.dat'
    
    ref = open(ref_log_book,'w')
    unf = open(unf_log_book,'w')
    
    total_left_solution  = 0.0
    total_right_solution = 0.0
    
    ref.write('%-8s\t%-8s\t%-8s\t%-8s\t%-8s\n'%('Number','Total(uL)','Left(uL)','Right(uL)','[Den]'))
    unf.write('%-8s\t%-8s\t%-8s\t%-8s\t%-8s\n'%('Number','Total(uL)','Left(uL)','Right(uL)','[Den]'))
    
    print 'Preparing refolding solutions'
    input = raw_input("Are you ready for refolding solutions?")
    #First prepare refolding solutions
    num_ref_points  = int((RIGHT_POINT - first_point)/SPACING_REF) + 1
    for i in range(num_ref_points):
        input = raw_input("Refolding solution "+str(i+1))
        target_conc  = first_point + i*SPACING_REF
        diluent_conc = ((DILUTION+1.0)*target_conc - UNFOLDED_SOLUTION)/DILUTION
        left_vol   = SF_DILUENT_VOL*(diluent_conc - RIGHT_SOLUTION)/(LEFT_SOLUTION - RIGHT_SOLUTION)
        right_vol  = SF_DILUENT_VOL - left_vol
        total_left_solution  +=left_vol
        total_right_solution +=right_vol
        left_actual,right_actual,actual_conc = fill_disp_both_oversize_simulate([left_vol,right_vol])
        actual_vol = left_actual+right_actual
        print "Total:%.3f\tLeft:%.3f\tRight:%.3f\tConc:%.3f"%(actual_vol,left_actual,right_actual,actual_conc)
        ref.write("%d\t%.3f\t%.3f\t%.3f\t%.3f\n"%(i+1,actual_vol,left_actual,right_actual,actual_conc))
    
    print 'Preparing unfolding solutions'
    input = raw_input("Are you ready for unfolding solutions?")
    #Now prepare unfolding solutions
    num_unf_points  = int((final_point - LEFT_POINT)/SPACING_UNF) + 1
    for i in range(num_unf_points):
        input = raw_input("Unfolding solution "+str(i+1))
        target_conc = LEFT_POINT + i*SPACING_UNF
        diluent_conc = ((DILUTION+1.0)*target_conc - FOLDED_SOLUTION)/DILUTION
        left_vol   = SF_DILUENT_VOL*(diluent_conc - RIGHT_SOLUTION)/(LEFT_SOLUTION - RIGHT_SOLUTION)
        right_vol  = SF_DILUENT_VOL - left_vol
        total_left_solution  +=left_vol
        total_right_solution +=right_vol
        
        left_actual,right_actual,actual_conc = fill_disp_both_oversize_simulate([left_vol,right_vol])
        print "Total:%.3f\tLeft:%.3f\tRight:%.3f\tConc:%.3f"%(actual_vol,left_actual,right_actual,actual_conc)
        unf.write("%d\t%.3f\t%.3f\t%.3f\t%.3f\n"%(i+1,actual_vol,left_actual,right_actual,actual_conc))
    
    print 'Preparing FOLDED sample'
    input = raw_input("Are you ready for FOLDED sample?")
    #Now prepare folded solution
    left_vol  =  ((SF_SAMPLE_VOL-PROTEIN_VOL)*(FOLDED_SOLUTION - RIGHT_SOLUTION)+(FOLDED_SOLUTION*PROTEIN_VOL))/(LEFT_SOLUTION - RIGHT_SOLUTION)
    right_vol =  SF_SAMPLE_VOL - PROTEIN_VOL - left_vol
    left_actual,right_actual,actual_conc = fill_disp_both_oversize_simulate([left_vol,right_vol])
    actual_vol = left_actual+right_actual
    total_left_solution  +=left_vol
    total_right_solution +=right_vol
    print "Left:%.3f\tRight:%.3f\tConc:%.3f\t Protein Vol:%.3f"%(left_actual,right_actual,actual_conc,PROTEIN_VOL)
    unf.write("\nFOLDED SAMPLE\tTOTAL:%.3f\tLEFT:%.3f\tRIGHT:%.3f\tCONC:%.3f\tADD PROTEIN(uL)\t%.3f\n"%(actual_vol,left_actual,right_actual,actual_conc,PROTEIN_VOL))
    print "TOTAL FOLDED SAMPLE VOLUME %.3f\t FINAL CONC: %.3f"%(actual_vol+PROTEIN_VOL,actual_conc*actual_vol/(actual_vol+PROTEIN_VOL))
    
    print 'Preparing UNFOLDED sample'
    input = raw_input("Are you ready for UNFOLDED sample?")
    #Now prepare unfolded solution
    left_vol  =  ((SF_SAMPLE_VOL-PROTEIN_VOL)*(UNFOLDED_SOLUTION - RIGHT_SOLUTION)+(UNFOLDED_SOLUTION*PROTEIN_VOL))/(LEFT_SOLUTION - RIGHT_SOLUTION)
    right_vol =  SF_SAMPLE_VOL - PROTEIN_VOL - left_vol
    left_actual,right_actual,actual_conc = fill_disp_both_oversize_simulate([left_vol,right_vol])
    actual_vol = left_actual+right_actual
    total_left_solution  +=left_vol
    total_right_solution +=right_vol
    print "Left:%.3f\tRight:%.3f\tConc:%.3f\t Protein Vol:%.3f"%(left_actual,right_actual,actual_conc,PROTEIN_VOL)
    ref.write("\nUNFOLDED SAMPLE\tTOTAL:%.3f\tLEFT:%.3f\tRIGHT:%.3f\tCONC:%.3f\tADD PROTEIN(uL)\t%.3f\n"%(actual_vol,left_actual,right_actual,actual_conc,PROTEIN_VOL))
    print "TOTAL UNFOLDED SAMPLE VOLUME %.3f\t FINAL CONC: %.3f"%(actual_vol+PROTEIN_VOL,actual_conc*actual_vol/(actual_vol+PROTEIN_VOL))
    print "TOTAL REFOLDING SOLUTIONS:%3d\tTOTAL UNFOLDING SOLUTIONS:%3d"%(num_ref_points,num_unf_points)
    print "TOTAL LEFT(uL):%.3f\tTOTAL RIGHT(uL):%.3f\tTOTAL UNFOLDED PROTEIN(uL):%.3f\t TOTAL FOLDED PROTEIN(uL):%.3f"%(total_left_solution,total_right_solution,400*num_ref_points,400*num_unf_points)
    
    ref.close()
    unf.close()
    
#--------------------------------------------------------------
#GLOBAL VARIABLES
#--------------------------------------------------------------


# configure the serial connections (the parameters differs on the device you are connecting to)
SER = serial.Serial(
    port='/dev/tty.usbserial',          #For serial port
    parity=serial.PARITY_ODD,
    baudrate=9600,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.SEVENBITS
)

#Open the port

SER.open()
SER.isOpen()

#Collection of routines
ROUTINES = ['read_port',
            'home_syringes',
            'initialize',
            'set_resolution',
            'check_left_syringe',
            'check_right_syringe',
            'fill_disp_left_syringe',
            'fill_disp_right_syringe',
            'fill_disp_both_syringes',
            'fill_disp_both_oversize',
            'prime_syringes',
            'set_left_sample',
            'set_right_sample',
            'set_mid_point',
            'set_left_point',
            'set_right_point',
            'prep_sf_solutions',
            'prep_sf_solutions_simulate',
            'set_dilution',
            'set_spacing',
            'set_diluent_vol',
            'set_sample_vol'
            ]

# Initialize the syringe sizes first in uL units
LEFT_SYRINGE      = 2500.0
RIGHT_SYRINGE     = 2500.0
RESOLUTION        = 1
FULL_STEPS        = 2000
DILUTION          = 10.0
LEFT_SOLUTION     = 0.0
RIGHT_SOLUTION    = 8.02
LEFT_POINT        = 0.4
MIDPOINT          = 0.8
RIGHT_POINT       = 1.2

FOLDED_SOLUTION   = 0.0
UNFOLDED_SOLUTION = 2.2
PROTEIN_VOL       = 1000.0

#The maximum denaturation concentration we want to reach
#If final_point value is bigger than MAX_DENATURANT, final_point is assigned to MAX_DENATURANT
MAX_DENATURANT    = 12.0

#Do not modify these values
SPACING_REF    =  0.15
SPACING_UNF    =  0.25
SF_DILUENT_VOL =  7800
SF_SAMPLE_VOL  = 12000

#Left Syringe
input_error = True
while input_error:
    input = raw_input("LEFT  SYRINGE SIZE in uL (2500uL) : ")

    if is_number(input):
        LEFT_SYRINGE = float(input)
        input_error  = False
    elif input == '':
        input_error  = False
    else:
        print "INPUT ERROR!"
        
#Right Syringe
input_error = True
while input_error:
    input = raw_input("RIGHT SYRINGE SIZE in uL (2500uL) : ")

    if is_number(input):
        RIGHT_SYRINGE = float(input)
        input_error  = False
    elif input == '':
        input_error  = False
    else:
        print "INPUT ERROR!"

#Right Syringe
input_error = True
while input_error:
    input = raw_input("RESOLUTION(default:low)  (l/h)  : ")

    if input == 'h':
        RESOLUTION = 1
        FULL_STEPS = 2000
        input_error  = False
    elif input == '' or input == 'l':
        input_error  = False
    else:
        print "INPUT ERROR!"


print 'Enter your commands below.\r\nInsert "exit" to leave the application.'

input = 1
while 1 :
    # get keyboard input
    input = raw_input(">> ")
    function,params  = parse_command(input)
    if function == 'exit':
            SER.close()
            exit()
    elif function in ROUTINES:
        func = globals()[function]
        func(params)
    else:
        # send the character to the device
        SER.write(input+'\r\n')
        #Now read the port after 1s 
        literal,ascii = read_port()
        if len(literal) > 0:
            print ">>Literal:"+'\t'.join(literal)
            print ">>ASCII  :"+'\t'.join([str(x) for x in ascii])
        
