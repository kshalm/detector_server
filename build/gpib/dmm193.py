from __future__ import print_function
from builtins import object
#!/usr/bin/env python
# Keithley 193 system DMM

from Gpib import *
import time


class dev(object):
    def __init__(self, name):
        """Connect to SR400"""
        self.meter = Gpib(name)
        meter = self.meter
        #meter.write('ZERO:AUTO OFF')
    def write(self, str):
        self.meter.write(str)

    def read(self):
        a = self.meter.read(100)
        return int(a)

    def quickread(self):
        self.meter.write('G1X')
        msg = self.meter.read()
        return float(msg)

    def close(self):
        """End communication with the DMM"""
        self.meter.close()


if (__name__ == '__main__'):
    dev1 = dev('dev6')
    a = dev1.quickread()
    print(a)
    dev1.close()
