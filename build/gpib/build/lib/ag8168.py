from __future__ import print_function
from builtins import object
#!/usr/bin/env python
from Gpib import *
import time
import ctypes
import string


class dev(object):
    def __init__(self, name):
        """Connect to and reset an agilent 8166A"""
        self.meter = Gpib(name)
        meter = self.meter
        #self.reset()
        #meter.write('ZERO:AUTO OFF')

    def enable(self):
        msg = 'OUTP:STAT ON'
        self.meter.write(msg)

    def disable(self):
        msg = 'OUTP:STAT OFF'
        self.meter.write(msg)

    def get_stat(self):
        try:
            msg = 'OUTP:STAT?'
            self.meter.write(msg)
            reading = self.meter.read()
            return int(reading)
        except self.meter.error:
            return -1

    def set_source_lambda(self, wav):
        """Set the wavelength in nm"""
        msg = 'SOUR:WAVE %.3f NM' % (wav)
        self.meter.write(msg)

    def set_lambda(self, wav):
        self.set_source_lambda(wav)

    def get_source_lambda(self):
        """Get the wavelength"""
        try:
            msg = ':SOUR:WAVE?'
            self.meter.write(msg)
            reading = self.meter.read()
            print(reading)
            return float(reading)
        except self.meter.error:
            return None

    def reset(self):
        """Reset the DMM and it's registers."""
        self.meter.write('*RST')
        self.meter.write('*CLS')

    def close(self):
        """End communication with the DMM"""
        self.meter.close()


if (__name__ == '__main__'):
    dev1 = dev('dev10')
    dev1.disable()
    time.sleep(1)
    dev1.enable()
    dev1.set_source_lambda(1550)
    dev1.close()
