from __future__ import print_function
from builtins import object
#!/usr/bin/env python
import Gpib
import string, os, sys, time


class device(object):
    def __init__(self, addr, serialport=''):
        #def __init__(self, name):
        self.k2k, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        #self.k2k = Gpib(name)
        k2k = self.k2k
        k2k.write('*RST')
        k2k.write('*CLS')
        k2k.write('FUNC \'VOLT:AC\'')
        #print self.port, self.addr, self.p
    def read(self):
        k2k = self.k2k
        k2k.write('READ?')
        #hp.trigger()
        '''
    poll = hp.rsp()
    print "Poll ",ord(poll)
    while (ord(poll) < 128):
      poll = hp.rsp()
      print "Poll ",ord(poll)
    '''
        a = k2k.read()
        return string.atof(a)

    def close(self):
        self.k2k.close()


if (__name__ == '__main__'):
    dmm1 = device('dev21')
    a = dmm1.read()
    print(a)
    dmm1.close()
