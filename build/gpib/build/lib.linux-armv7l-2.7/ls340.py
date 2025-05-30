from __future__ import print_function
from builtins import object
#!/usr/bin/env python
from Gpib import *


class dev(object):
    def __init__(self, name):
        """Connect to and reset a LS 340"""
        self.meter = Gpib(name)
        meter = self.meter
        #self.reset()
        #meter.write('ZERO:AUTO OFF')

    def krdg_a(self):
        """Take a kelvin reading from channel a"""
        try:
            self.meter.write('KRDG? A')
            reading = self.meter.read()
            return float(reading.replace('+', ''))
        except self.meter.error:
            return None

    def krdg_b(self):
        """Take a kelvin reading from channel b"""
        try:
            self.meter.write('KRDG? B')
            reading = self.meter.read()
            return float(reading.replace('+', ''))
        except self.meter.error:
            return None

    def srdg_b(self):
        """Take a kelvin reading from channel b"""
        try:
            self.meter.write('SRDG? B')
            reading = self.meter.read()
            return float(reading.replace('+', ''))
        except self.meter.error:
            return None

    def htr(self):
        """Take a heater reading"""
        try:
            self.meter.write('HTR?')
            reading = self.meter.read()
            return float(reading.replace('+', ''))
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
    dev1 = dev('dev12')
    a = dev1.krdg_a()
    b = dev1.krdg_b()
    bb = dev1.srdg_b()
    print('%.2f  %.2f  %.2f' % (a, b, bb))
    dev1.close()
