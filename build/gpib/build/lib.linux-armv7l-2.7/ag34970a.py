from __future__ import print_function
from builtins import str
from builtins import object
#!/usr/bin/env python
from Gpib import *
import time
import string


class dev(object):
    def __init__(self, name='dev9'):
        """Connect to and reset an agilent 8166A"""
        self.meter = Gpib(name)
        meter = self.meter
        #self.reset()
        #meter.write('ZERO:AUTO OFF')

    def identify(self):
        msg = '*IDN?\n'
        self.meter.write(msg)
        self.meter.read()

    def reset(self):
        self.meter.write('ROUT:OPEN (@101:122)')
        self.meter.write('ROUT:OPEN (@197)')
        self.meter.write('ROUT:OPEN (@198)')
        self.meter.write('ROUT:OPEN (@199)')
        msg = 'All switches opened'
        print(msg)

    def switch(self, chNum):
        n1 = 100 + chNum
        cmd1 = 'ROUT:CLOSE (@' + str(n1) + ')'
        print(cmd1)
        self.meter.write(cmd1)
        msg = 'channel ' + str(n1)
        print(msg)

    def close(self):
        """End communication with the DMM"""
        self.meter.close()
