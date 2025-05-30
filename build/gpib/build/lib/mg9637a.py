from __future__ import print_function
from builtins import object
#!/usr/bin/env python
from Gpib import *
import time


class dev(object):
    def __init__(self, name):
        self.meter = Gpib(name)
        meter = self.meter

    def setModeCW(self):
        self.meter.write('MCW')

    def setWavelength(self, wavelength):
        str = 'WCNT %.3fnm ' % wavelength
        self.meter.write(str)
        time.sleep(0.5)

    def getWavelength(self):
        self.meter.write('OUTW?')
        return (float(self.meter.read()) * 1e9)

    def close(self):
        """End communication with the DMM"""
        self.meter.close()


if (__name__ == '__main__'):
    dev1 = dev('dev13')
    dev1.setModeCW()
    dev1.setWavelength(1541.123)
    print(dev1.getWavelength())
    dev1.close()
