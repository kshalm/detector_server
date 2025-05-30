from __future__ import print_function
from builtins import object
#!/usr/bin/env python
from Gpib import *
import string, os, sys, time, struct


class device(object):
    def __init__(self, addr, serialport=''):

        # -- Add general declaration 3/3/2015 --
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        self.hp = self.meter
        # -- end --

        #self.hp = Gpib(name)
        hp = self.hp
        hp.write('PRESET FAST')
        hp.write('OFORMAT ASCII')
        #hp.write('PRESET FAST')
        hp.write('DISP ON')
        #hp.write('ACV 0.1')
        #hp.write('SETACV ANA')
        #hp.write('ACBAND 500,100e3')
        hp.write('END ALWAYS')
        hp.write('TRIG LINE')
        #hp.trigger()
        hp.write('NPLC 0')
        hp.write('NRDGS 1,AUTO')
        #hp.write('TARM HOLD')
        #hp.write('RANGE 1')                                                         
    def setupsint(self):
        self.hp.write('MFORMAT SINT')
        self.hp.write('OFORMAT SINT')

    def read(self):
        hp = self.hp
        hp.write('TARM SGL')
        poll = hp.rsp()
        #print "Poll ",ord(poll)
        while (ord(poll) < 128):
            poll = hp.rsp()
            time.sleep(0.001)
            #print "Poll ",ord(poll)
        a = hp.read()
        #print len(a)
        return string.atof(a)
        #hp.write('TARM AUTO') 
        #hp.write('TRIG SYN') 
        #hp.write('NRDGS 1,AUTO')
    def readsint(self):
        hp = self.hp
        hp.write('TARM SGL')
        poll = hp.rsp()
        #print "Poll ",ord(poll)
        while (ord(poll) < 128):
            poll = hp.rsp()
            time.sleep(0.001)
            #print "Poll ",ord(poll)
        a = hp.read()
        b = struct.unpack('>h', a)
        return b[0]

    def readiscale(self):
        self.hp.write('ISCALE?')
        a = self.hp.read()
        return string.atof(a)

    def close(self):
        self.hp.close()


if (__name__ == '__main__'):
    dmm1 = device('dev22')
    a = dmm1.read()
    print(a)
    dmm1.close()
