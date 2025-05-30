from __future__ import print_function
from builtins import str
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
        poll = hp.rsp()
        print(len(poll))

    def read(self):
        hp = self.hp
        #hp.write('READ?')
        #hp.trigger()
        '''
    poll = hp.rsp()
    print "Poll ",ord(poll)
    while (ord(poll) < 128):
      poll = hp.rsp()
      print "Poll ",ord(poll)
    '''
        a = hp.read(65536)
        return a

#   return string.atof(a)

    def write(self, stri):
        hp = self.hp
        hp.write(str(stri))

    def close(self):
        self.hp.close()

if (__name__ == '__main__'):

    scope = device('dev1')
    a = scope.read()
    print(a)
    scope.close()
