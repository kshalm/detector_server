from __future__ import print_function
from builtins import str
from builtins import object
#!/usr/bin/env python
from Gpib import *
import time
import ctypes


class dev(object):
    def __init__(self, name):
        """Connect to and reset an agilent 8166A"""
        self.meter = Gpib(name)
        meter = self.meter
        #self.reset()
        #meter.write('ZERO:AUTO OFF')

    def set_att(self, slot, att):
        """Set the attenuation"""
        msg = 'INP%s:ATT %s' % (str(slot), str(att))
        self.meter.write(msg)

    def set_lambda(self, slot, wav):
        """Set the wavelength in nm"""
        msg = 'INP%s:WAV %sE-9' % (str(slot), str(wav))
        self.meter.write(msg)

    def get_att(self, slot):
        """Get the attenuation"""
        print("hello")
        try:
            msg = ':INP%s:ATT?' % (str(slot))
            self.meter.write(msg)
            reading = self.meter.read()
            return float(reading)
        except self.meter.error:
            return None

    def get_lambda(self, slot):
        """Get the wavelength"""
        try:
            msg = ':INP%s:WAV?' % (str(slot))
            self.meter.write(msg)
            reading = self.meter.read()
            print(reading)
            return float(reading)
        except self.meter.error:
            return None

    def get_pow(self, slot):
        """Get the power"""
        wait = 1
        while (wait):
            try:
                msg = ':READ%s:POW?' % (str(slot))
                self.meter.write(msg)
                #poll = self.meter.ibrsp()
                #loop =0 
                #while (ord(poll)==0):
                #print "nothing ready"
                #poll = self.meter.ibrsp()
                #loop = loop+1
                #if loop==200:
                #poll = chr(16) 
                ##print ord(poll)
                #if (loop>100):
                #print "Loop: %d"%loop
                reading = self.meter.read()
                #poll = self.meter.ibrsp()
                #print length(poll)
                return float(reading)
            except:
                if (wait == 3):
                    return -1
                    print("error reading power: slot %d:%d:<%s>" %
                          (slot, poll, reading))
                wait = wait + 1

    def set_powlambda(self, slot, wav):
        """Set the wavelength in nm"""
        msg = 'SENS%s:POW:WAV %snm' % (str(slot), str(wav))
        self.meter.write(msg)

    def reset(self):
        """Reset the DMM and it's registers."""
        self.meter.write('*RST')
        self.meter.write('*CLS')

    def close(self):
        """End communication with the DMM"""
        self.meter.close()


if (__name__ == '__main__'):
    dev1 = dev('dev9')
    a = dev1.get_lambda(0)
    print('%.2e' % a)
    dev1.close()
