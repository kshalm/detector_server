from __future__ import print_function
from builtins import object
#!/usr/bin/env python
from Gpib import *
import string, os, sys, time


class device(object):
    def __init__(self, addr, serialport=''):

        # -- Add general declaration 3/3/2015 --
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        self.hp = self.meter
        # -- end --

        #self.hp = Gpib(name)
        hp = self.hp
        #hp.write('*RST')
        #hp.write('*CLS')
        #hp.write('ZERO:AUTO OFF')
        #hp.write('TRIG:SOUR BUS')

    def read(self):
        try:
            hp = self.hp
            hp.write('READ?')
            a = hp.read()
            return string.atof(a)
        except hp.error:
            return None

    def close(self):
        self.hp.close()


if (__name__ == '__main__'):
    dmm1 = device('dev21')
    a = dmm1.read()
    print(a)
    dmm1.close()
