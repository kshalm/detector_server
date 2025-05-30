from __future__ import print_function
from builtins import str
from builtins import range
from builtins import object
#!/usr/bin/env python
# from Gpib import *
from Gpib_prologix_nt_ver2 import *
import serial


class dmm(object):
    def __init__(self, addr, serialport):
        """Connect to and reset a 3401A DMM"""
        #self.meter = Gpib(name) 
        self.meter = Gpib(addr, serialport)
        meter = self.meter
        self.port = serialport
        #self.reset()
        #meter.write('ZERO:AUTO OFF')

    def setAC(self, range='DEF', resolution=None):
        """Set the DMM to measure DC voltage.
    
        range      - a voltage around which the range will be set
        resolution - the desired resolution in volts
    
        Either of these values can be set to 'MIN', 'MAX', or 'DEF'
        'DEF' will give autoranging or 5 1/2 digits.

        Resolution for AC measurements is actually fixed at 6 1/2 digits.
        
        """
        if resolution != None:
            self.meter.write('CONF:VOLT:AC %s,%s' %
                             (str(range), str(resolution)))
        else:
            self.meter.write('CONF:VOLT:AC %s' % str(range))
        self.meter.write('TRIG:SOURCE IMMEDIATE')

    def setDC(self, range='DEF', resolution=None):
        """Set the DMM to measure DC voltage.
    
        range      - a voltage around which the range will be set
        resolution - the desired resolution in volts
    
        Either of these values can be set to 'MIN', 'MAX', or 'DEF'
        'DEF' will give autoranging or 5 1/2 digits.
        
        """
        if resolution != None:
            self.meter.write('CONF:VOLT:DC %s,%s' %
                             (str(range), str(resolution)))
        else:
            self.meter.write('CONF:VOLT:DC %s' % str(range))
        self.meter.write('TRIG:SOURCE IMMEDIATE')

    def setR(self, range='DEF', resolution=None):
        """Set the DMM to measure resistance.
    
        range      - a voltage around which the range will be set
        resolution - the desired resolution in ohms.
    
        Either of these values can be set to 'MIN', 'MAX', or 'DEF'
        'DEF' will give autoranging or 5 1/2 digits?
        
        """
        if resolution != None:
            self.meter.write('CONF:RESISTANCE %s,%s' %
                             (str(range), str(resolution)))
        else:
            self.meter.write('CONF:RESISTANCE %s' % str(range))
        self.meter.write('TRIG:SOURCE IMMEDIATE')

    def setDelay(self, delay):
        """Set the delay before readings are taken.

        delay - Either a delay in seconds or 'MIN', 'MAX' or 'AUTO'

        """
        if delay == 'AUTO':
            self.meter.write('TRIG:DELAY:AUTO ON')
        else:
            self.meter.write('TRIG:DELAY %s' % str(delay))

    def read(self):
        """Take a reading from the DMM"""
        try:
            self.meter.write('READ?')
            reading = self.meter.read()
            while len(reading) == 0:
                #print 'trying to read again'
                reading = self.meter.read()
            #print '%d:%s'%(len(reading),reading)
            return float(reading)
        except self.meter.error:
            return None

    def display(self, message=None):
        """Set the text displayed by the DMM.
        
        Call without any arguments to clear the display.

        """

        if message == None:
            self.meter.write('DISP:TEXT:CLEAR')
        else:
            self.meter.write('DISP:TEXT "%s"' % message)

    def beep(self):
        """Make the DMM beep once."""

        self.meter.write('SYST:BEEP')

    def checkErr(self):
        """Check the DMM's Error queue.

        '+0,"No error"\n' is returned if there are no errors.

        """
        self.meter.write('SYST:ERR?')
        err = self.meter.read()
        return err

    def reset(self):
        """Reset the DMM and it's registers."""
        self.meter.write('*RST')
        self.meter.write('*CLS')

    def close(self):
        """End communication with the DMM"""
        self.meter.loc()


if (__name__ == '__main__'):
    serialport = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
    #dmm1 = dmm('dev8')
    dmm1 = dmm(8, serialport)
    print(dmm1.meter.read())
    for i in range(10):
        print(dmm1.read())
    dmm1.close()
    serialport.close()
