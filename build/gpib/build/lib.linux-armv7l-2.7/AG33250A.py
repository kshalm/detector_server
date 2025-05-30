from __future__ import print_function
from builtins import str
from builtins import range
import Gpib
import time
import sys, os
import baseinst
import serial


class dev(baseinst.dev):
    def __init__(self, addr, serialport):
        """Connect to and reset"""
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        self.port = serialport
        self.meter.write('*IDN?')
        print(self.meter.read())

    def setFreq(self, val):
        self.meter.write('FREQ %f\n' % float(val))

    def getFreq(self):
        return self.meter.query('FREQ?')

    def setVpp(self, val):
        self.meter.write('VOLT %f\n' % float(val))

    def setHigh(self, val):
        self.meter.write('VOLT:HIGH %f\n' % float(val))

    def setLow(self, val):
        self.meter.write('VOLT:LOW %f\n' % float(val))

    def checkErr(self):
        """Check the Error queue.
    '+0,"No error"\n' is returned if there are no errors.

    """
        self.meter.write('SYST:ERR?')
        err = self.meter.read()
        return err

    def loadAwgInt(self, data):
        """ 
    Loads arb. waveform as a series of ints in range -2047 to +2047 
    Input data must be in this range
    Loads waveform to volitile memory must run SaveLoadedWaveformAs(FuncName)
    """
        if not ('int' in str(type(data[0]))):
            raise TypeError(
                "Wrong Data type for this function must be type int +/- 2047")
        if max(data) > 2047 or min(data) < -2047:
            raise ValueError("ADC Values out of range, must be in +/- 2047")
        msg = 'DATA:DAC VOLATILE'
        for point in data:
            app = ', ' + str(point)
            msg += app
        msg += '\n'
        self.meter.write(msg)

    def disableOut(self):
        """turns off awg output """
        self.meter.write('OUTPUT OFF\n')

    def enableOut(self):
        """turns on awg output """
        self.meter.write('OUTPUT ON\n')

    def getOutEnabled(self):
        return ('1' in self.meter.query('OUTPUT?\n'))

    def displayText(self, msg):
        self.meter.write('DISP:TEXT "' + msg + '"\n')

    def clearText(self):
        self.meter.write('DISP:TEXT ""\n')

    def loadAwgFloat(self, data):
        """ 
    Loads arb. waveform as a series of floats in range +/- 1 
    Input data must be in this range
    Loads waveform to volitile memory must run SaveLoadedWaveformAs(FuncName)
    """
        if not ('float' in str(type(data[0]))):
            if 'int' in str(type(data[0])):
                data = data * 1.0
            else:
                raise TypeError(
                    "Wrong Data type for this function must be type float +/- 1"
                )
        if max(data) > 1 or min(data) < -1:
            raise ValueError("Values out of range, must be in +/- 1")
        msg = 'DATA VOLATILE'
        for point in data:
            app = ', ' + str(point)
            msg += app
        msg += '\n'
        self.meter.write(msg)

    def getUserWaveforms(self):
        AWFs = self.meter.query('DATA:NVOLatile:CATalog?\n')[1:-2].split('","')
        return AWFs

    def SaveLoadedWaveformAs(self, FuncName):
        if not (self.checkNonVolMem()):
            print(
                "Memory full please remove a waveform before saving a new one")
            print("Found the follwing user programed waveforms:\n")
            print(self.getUserWaveforms())
        else:
            self.meter.write('DATA:COPY ' + FuncName + ',VOLATILE\n')

    def clrNonvolMem(self):
        self.meter.write('FUNC:USER EXP_FALL\n')
        self.meter.write("DATA:DEL ALL\n")

    def getBuiltInWaveforms(self):
        print("The AWG has the following built in:")
        print(["EXP_RISE", "EXP_FALL", "NEG_RAMP", "SINC", "CARDIAC"])
        return ["EXP_RISE", "EXP_FALL", "NEG_RAMP", "SINC", "CARDIAC"]

    def setArbWaveformOutput(self, waveformName=None):
        if waveformName == None:
            self.meter.write('FUNC:USER ' + waveformName + '\n')
            self.meter.write('FUNC:USER VOLATILE\n')

    def removeUserWavform(self, waveformName):
        self.meter.write('DATA:DEL ' + waveformName + '\n')

    def checkNonVolMem(self):
        '''
    Query the number of non-volatile memory slots available to store userdefined
    waveforms. Returns the number of memory slots available to store userdefined
    waveforms. Returns “0” (memory is full), “1”, “2”, “3”,
    or “4”. 
    '''
        free = int(self.meter.query('DATA:NVOL:FREE?\n'))
        print(free)
        return free

    def getStatReg(self):
        from math import log
        msg = ''
        resp = self.meter.query('STAT:QUES?')
        if resp == '':
            resp = '0'
        #print resp
        stat = int(resp)
        #print stat
        if stat == 0:
            r = 0
        else:
            r = int(log(stat, 2)) + 1
        for n in range(r):
            if 2**n == stat % (2**(n + 1)) - stat % (2**n):
                if n == 9:
                    msg += 'External timebase is being used'
                elif n == 8:
                    msg += 'Error occurred during cal'
                elif n == 7:
                    msg += 'Voltage overload on MOD IN connector'
                elif n == 5:
                    msg += 'Function generator has lost phase lock'
                elif n == 4:
                    msg += 'Internal temperature is too high'
                elif n == 0:
                    msg += 'Voltage overload on OUTPUT connector, the output has been disabled'
                else:
                    msg += 'Invalid Registry Value Read, Using Wrong Class?'
                msg += ', '
        if msg != '':
            msg = msg[:-2]
        #print msg
        if stat != 0:
            self.meter.write('STAT:QUES:ENAB %d' % stat)
        return msg

    def writeconfig(self, fp):
        fp.write('# *IDN? Responce: %s\n' % self.identify())
        fp.write('# AWG status bit message: %s' % self.getStatReg())

    def close(self):
        self.meter.loc()


if (__name__ == '__main__'):
    vpp = 1.0
    vHigh = 1
    vLow = 0
    if len(sys.argv) > 1:
        vHigh = float(sys.argv[1])
        vLow = 0
    serialport = serial.Serial('COM4', 9600, timeout=0.5)
    addr = 12
    awg = dev(addr, serialport)
    print(awg.getFreq())
    print(awg.identify())
    c = False

    def close():
        dmm1.close()
        serialport.close()

    if c:
        close()
