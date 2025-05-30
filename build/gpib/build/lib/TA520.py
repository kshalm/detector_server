from __future__ import print_function
from builtins import object
#!/usr/bin/env python
from Gpib import *
import string, os, sys, time


class device(object):

    #def __init__(self, name):
    def __init__(self, addr, serialport=''):

        # -- Add general declaration 3/3/2015 --
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        self.ta = self.meter
        # -- end --

        # self.ta = Gpib(name)
        #self.name = name
    def setend(self, end):
        self.ta.write("MEM:END %d", end)

    def write(self, msg):
        return self.ta.write(msg)

    def read(self, len):
        try:
            a = self.ta.read(len)
            return a
        except self.ta.error:
            return None

    def readb(self, len):
        try:
            a = self.ta.readb(len)
            return a
        except self.ta.error:
            return None

    def setGateEventNum(self, num):
        self.ta.write(':SAMPLE:GATE:MODE EVENT')
        msg = ':SAMPLE:GATE:EVENT %d' % num
        self.ta.write(msg)

    def getGateEventNum(self):
        self.ta.write(':SAMPLE:GATE:EVENT?')
        msg = self.ta.read(100)
        #term = string.find(msg,chr(10))
        #return int(msg[0:term])
        return int(msg)

    def getMemSend(self):
        self.ta.write('MEM:SEND?')
        loop = 1
        debug = 1
        while (loop):
            c = self.ta.read(1)
            if debug:
                print('c: %c %d' % (c, ord(c)))
            if c == '#':
                loop = 0
        c = self.ta.read(1)
        msg = self.ta.read(8)
        if (debug == 1):
            print('binary mode len: %s' % msg)
        l = int(msg)
        loop = 1
        a = ''
        while (loop):
            if (l < 65535):
                a = a + self.ta.readb(l)
                loop = 0
            else:
                a = a + self.ta.readb(65535)
                l = l - 65535
            if (l == 0):
                break

        nl = self.ta.read(1000)
        if ord(nl[0]) != 10:
            print('POSSIBLE ERROR in BINARY TRANSFER')
        return a

    def close(self):
        self.ta.close()


if (__name__ == '__main__'):
    ta = device('dev2')
    ta.write('MEM?')
    a = ta.read(100)
    print(a)
