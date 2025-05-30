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
        self.vset = -1
        self.v = -1
        self.i = -1

    def read(self):
        hp = self.hp
        wait = 1
        while (wait == 1):
            try:
                hp.write('VOLT?')
                a = hp.read()
                self.vset = float(a)
                hp.write('MEAS:VOLT?')
                a = hp.read()
                self.v = float(a)
                hp.write('MEAS:CURR?')
                a = hp.read()
                self.i = float(a)
                if (self.i == -1 or self.v == -1):
                    #return -1
                    print("Bad i or v from 6641")
                    wait = 1
                else:
                    wait = 0
            except:
                #return -1
                print("Gpib read error")
        return 0

    def setv(self, vset):
        hp = self.hp
        ret = self.read()
        if (abs(vset - self.v) > 0.9 or ret == -1):
            if (ret == -1):
                print('HP6641A device read failed, command ignored.')
                return -1
            print('dV > 0.9V, command ignored.')
            return -1
        try:
            hp.write("VOLT " + str(vset))
        except hp.error:
            print('HP6641A device write failed.')

    def close(self):
        self.hp.close()


if (__name__ == '__main__'):
    dmm1 = device('dev5')
    a = dmm1.read()
    print(dmm1.v)
    print(dmm1.i)
    #  dmm1.setv(1.2)
    #  a = dmm1.read()
    #  print dmm1.v
    #  print dmm1.i
    dmm1.close()
