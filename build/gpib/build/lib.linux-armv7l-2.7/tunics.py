from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import object
#!/usr/bin/env python
from Gpib import *
import time
import ctypes
import string


class dev(object):
    def __init__(self, name):
        """Connect to and reset an agilent Tunics laser"""
        self.meter = Gpib(name)
        meter = self.meter
        #self.reset()
        #meter.write('ZERO:AUTO OFF')

    def enable(self):
        msg = 'ENABLE'
        self.meter.write(msg)
        time.sleep(2)

    def disable(self):
        msg = 'DISABLE'
        self.meter.write(msg)
        time.sleep(0.1)

    def set_source_lambda(self, wav):
        self.set_lambda(wav)

    def set_lambda(self, wav):
        """Set the wavelength in nm"""
        msg = 'L=%.3f\n' % (wav)
        self.meter.write(msg)
        time.sleep(1)

    def get_lambda(self):
        """Get the wavelength"""
        try:
            msg = 'L?'
            self.meter.write(msg)
            time.sleep(1)
            reading = self.meter.read()
            #print reading
            return float(reading[2:])
        except self.meter.error:
            return None

    def reset(self):
        """Reset the DMM and it's registers."""
        self.meter.write('*RST')
        self.meter.write('*CLS')

    def close(self):
        """End communication with the DMM"""
        self.meter.close()

    def identify(self):
        self.meter.write('*IDN?')
        time.sleep(1)
        laserid = self.meter.read()
        return laserid

    def set_pwr(self, las_pwr):
        """Set laser power"""
        msg = 'P=%.3f\n' % (las_pwr)
        self.meter.write(msg)

    def get_pwr(self):
        """Get the wavelength"""
        msg = 'P?'
        self.meter.write(msg)
        time.sleep(0.1)
        reading = self.meter.read()
        return reading

    def writeconfig(self, f):
        f.write('#Laser is ' + self.identify().strip() + '\n')
        return None


if (__name__ == '__main__'):
    dev1 = dev('dev11')
    dev1.set_lambda(1547)
    a = dev1.get_lambda()
    print(a)
    dev1.close()
