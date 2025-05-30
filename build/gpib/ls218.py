from __future__ import print_function
from builtins import object
#!/usr/bin/env python
from Gpib import *
import time


class dev(object):
    def __init__(self, name):
        """Connect to SR400"""
        self.meter = Gpib(name)
        meter = self.meter
        #self.reset()
        #meter.write('ZERO:AUTO OFF')
    def write(self, str):
        self.meter.write(str)

    def read(self):
        a = self.meter.read(100)
        return a

    def getTemps(self):
        self.write('KRDG?')
        msg = self.read()
        vals = []
        while (len(vals) < 5):
            a = float(msg[0:msg.find(',')])
            msg = msg[(msg.find(',') + 2):]
            vals = vals + [a]
        return vals

    def close(self):
        """End communication with the DMM"""
        self.meter.close()


if (__name__ == '__main__'):
    dev1 = dev('dev11')
    kelvins = dev1.getTemps()
    for a in kelvins:
        print(a)
    dev1.close()
