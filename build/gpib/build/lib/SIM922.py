#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
from builtins import object
from past.utils import old_div
import sys, os, string, time
import threading
from Gpib import *
import SIM900


class device(object):
    def __init__(self, name, channel):
        """Connect to SIM922"""
        self.sim900 = SIM900.device(name)
        self.channel = channel

    def setcal(self, diode_num, VT_curve_file):
        self.sim900.clearbuf(self.channel)
        while True:
            try:
                self.sim900.write(self.channel, 'VOLT? %d' % (diode_num))
                time.sleep(0.1)
                self.sim900.getval(self.channel)
                break
            except:
                print('Having trouble talking to SIM922')
                time.sleep(0.1)

        while True:
            try:
                self.sim900.write(self.channel, 'CINI %d,0' % (diode_num))
                time.sleep(0.1)

                fid = open(VT_curve_file, 'r')
                V = []
                T = []
                ivec = []
                tablelen = 0
                allines = fid.readlines()
                for line in allines:
                    lndat = string.split(line)
                    lndat2 = []
                    for ln in lndat:
                        if ln != '':
                            lndat2.append(ln)
                    T.append(float(lndat2[0]))
                    V.append(float(lndat2[1]))
                    ivec.append(tablelen)
                    tablelen = tablelen + 1
                V.reverse()
                T.reverse()
                time.sleep(0.1)
                for i in ivec:
                    self.sim900.write(self.channel, 'CAPT %d,%0.6f,%0.6f' %
                                      (diode_num, V[i], T[i]))
                    time.sleep(0.1)

                self.sim900.write(self.channel, 'CURV %d,1' % (diode_num))
                time.sleep(0.01)
                break
            except:
                print('Problem setting calibration curve ')
                time.sleep(0.01)

        return 0

    def gettemp(self, simchannels):
        return self.getvalues('TVAL', simchannels)

    def getvoltage(self, simchannels):
        valsin = self.getvalues('VOLT', simchannels)
        valsout = []
        # kind of a kludge, sometimes if V<1 it registers as V*10.  fix that:
        for val in valsin:
            if val > 1.7 and val < 10.0:
                val = old_div(val, 10.0)
            valsout.append(val)
        return valsout

    def getvalues(self, getstr, simchannels):
        delaytime = 0.01
        val = []
        time.sleep(delaytime)
        for simchannel in simchannels:
            #while True:
            #  try:
            #    self.sim900.getval(self.channel)
            #    time.sleep(0.05)
            #  except:
            #    break
            while True:
                try:
                    value = 0
                    while value == 0:
                        self.sim900.clearbuf(self.channel)
                        time.sleep(delaytime)
                        self.sim900.write(self.channel, '%s? %d' %
                                          (getstr, simchannel))
                        time.sleep(delaytime)
                        value = self.sim900.getval(self.channel)
                        #print val
                        value = float(value)
                        time.sleep(delaytime)
                    val.append(value)
                    break
                except:
                    print('Problem with getting %s ' % getstr)
                    time.sleep(delaytime)
        return val


if __name__ == '__main__':
    sim = device('dev2', 5)
    res = sim.getvoltage([1, 2, 3])
    print(res)
