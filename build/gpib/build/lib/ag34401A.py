from __future__ import print_function
from builtins import str
from builtins import object
#!/usr/bin/env python
import Gpib
import time
import ctypes
import string


class dev(object):
    def __init__(self, addr, serialport=''):
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        meter = self.meter
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

    def get_volt(self):
        return self.read()

    def read(self):
        """Take a reading from the DMM"""
        try:
            #if True:
            self.meter.write('READ?')
            while True:
                if self.meter.rsp() & 16:
                    break
                time.sleep(0.1)
            while True:
                #print 'spoll',dmm1.meter.rsp()
                #time.sleep(1)
                msg = self.meter.read(100).strip()
                if len(msg) > 0:
                    #print len(msg),msg
                    break
            #reading = self.meter.read()
            #return float(reading)
            return float(msg)
        #else:
        except:
            self.checkErr()

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

    def setInt(self, int_time):
        """Set Integration Time 
            Only the integral number of power line cycles 
            (1, 10, or 100 PLCs)provide normal mode 
            (line frequency noise) rejection"""
        self.meter.write('FUNC?')
        func = self.meter.read()[1:-2]
        if int_time in [.02, .2, 1, 10, 100, 'MIN', 'min', 'MAX', 'max']:
            self.meter.write(func + ':' + str(int_time))
        else:
            print(
                'ERROR: invalid intigration time (default 10 PLC) \n valid integration time inputs are .02,.2,1,10,100,\'MIN\',\'min\',\'MAX\',\'max\''
            )
            print('proceeding without change')

    def identify(self):
        msg = '*IDN?'
        self.meter.write(msg)
        time.sleep(0.1)
        return self.meter.read().strip()

    def writeconfig(self, f):
        msg = self.identify()
        #f.write('# Agilent 86142a in slot %d\n'%(self.slot))
        #f.write('#    ID: %s\n'%msg)
        f.write('# %s\n' % msg)
        self.meter.write('CONF?')
        msg = self.meter.read(1000)
        msg = msg.strip()
        print('conf', msg)
        f.write('# CONF: %s\n' % msg)
        f.flush()

    def close(self):
        """End communication with the DMM"""
        self.meter.loc()


if (__name__ == '__main__'):
    import serial
    #serialport = serial.Serial('/dev/ttyUSB1',115200,timeout=0.5)
    #serialport = serial.Serial('/dev/ttyUSB1',115200,timeout=0.5)
    serialport = '/dev/ttyUSB1'
    dmm1 = dev(22, serialport)
    print(dmm1.get_volt())
    #dmm1 = dmm('dev18')
    #~ dmm1.meter.write('CONF:VOLT:DC 1,MIN')
    #~ dmm1.meter.write('CONF?')
    #~ print(dmm1.meter.read(100))
    #~ dmm1.meter.write('FUNC \"VOLT:DC\"')
    #~ dmm1.meter.write('FUNC?')
    #~ print(dmm1.meter.read(100))
    #~ a = dmm1.read()
    #~ print(a)
    """
        dmm1.meter.write('READ?')
        import time
        while True:
            if dmm1.meter.rsp() & 16:
                break;
            time.sleep(0.1)
        while True:
            print 'spoll',dmm1.meter.rsp()
            #time.sleep(1)
            msg =  dmm1.meter.read(100)
            if len(msg)>0:
                print len(msg),msg
                break;
        """
    dmm1.close()
