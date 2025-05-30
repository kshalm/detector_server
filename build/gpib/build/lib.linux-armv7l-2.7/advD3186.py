# -*- coding: utf-8 -*-
"""
Created on Tue May 10 11:47:49 2016

@author: qittlab
"""
from __future__ import print_function
from builtins import str
from builtins import object
#!/usr/bin/env python
import sys, os, string, time
#from Gpib import *
#import serial
import threading
import Gpib


class dev(object):
    def __init__(self, addr, serialport=''):
        """Connect to D3186"""
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        self.WordBitLength = None
        self.meter.write("IDN?\n")
        print('initializing D3186')
        msg = self.meter.read(100)
        while msg != '':
            if 'D3186' in msg.split(','):
                print(msg)
            msg = self.meter.read(100)

    def setClkRate(self, val):
        ''' Clock rate in MHz'''
        if val > 12000:
            self.meter.write('CR 12000\n')
        elif val < 150:
            self.meter.write('CR 150\n')
        else:
            self.meter.write('CR %f\n' % float(val))

    def setOutput(self, val):
        if val == 0:
            self.meter.write('OUTOF\n')
        else:
            self.meter.write('OUTON\n')

    def setPattMode(self, val):
        vals = ['PRBS', 'WORD', 'FRAM']
        if val in vals:
            self.meter.write('%s\n' % str(val))
        else:
            print('Invalid Mode')

    def setPattStepCnt(self, val):
        vals = [7, 9, 10, 11, 15, 23, 31]
        if val in vals:
            self.meter.write('PB %d,0\n' % int(val))
        else:
            print('Invalid Step Value')

    def setMarkRatio(self, val):
        vals = ['0/8', '1/8', '1/4', '1/2', '8/8', '7/8', '3/4', '1/2B']
        if val in vals:
            self.meter.write('MR %s' % str(val))
        else:
            print('Invalid Mark Ratio')

    def setWordBitLength(self, val):
        if val > 2**23:
            self.meter.write('BL %d\n' % (2**23))
            self.WordBitLength = 2**23
        elif val < 1:
            self.meter.write('BL %d\n' % (2**0))
            self.WordBitLength = 2**0
        else:
            self.meter.write('BL %d\n' % int(val))
            self.WordBitLength = int(val)

    def setWord(self, val):
        outmsg = "WP 0,4,5C00\n"
        self.meter.write(outmsg)

    def check(self, query, val):
        self.meter.write(query)
        out = self.meter.read(100).split()[-1]
        if float(out) == val * 1e6:
            return True
        else:
            return False

    def close(self):
        self.meter.close()


if __name__ == "__main__":
    port = 'COM5'
    addr = 1
    d = dev(addr, port)
    d.close()
