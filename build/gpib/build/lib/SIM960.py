from __future__ import print_function
from builtins import object
#!/usr/bin/env python
import sys, os, string, time
import threading
from Gpib import *
import SIM900


class device(object):
    def __init__(self, name, channel):
        """Connect to SIM960"""
        self.sim900 = SIM900.device(name)
        self.channel = channel
        self.sim900.clearbuf(self.channel)
        time.sleep(0.1)

    def get_setpoint(self):
        while True:
            try:
                self.sim900.clearbuf(self.channel)
                time.sleep(0.1)
                self.sim900.write(self.channel, 'SETP?')
                time.sleep(2.0)
                val = self.sim900.getval(self.channel)
                #print val
                val = float(val)
                break
            except:
                print('Problem with getting setpoint ')
                time.sleep(0.2)
        return val

    def set_setpoint(self, value):
        while True:
            try:
                self.sim900.clearbuf(self.channel)
                time.sleep(0.1)
                self.sim900.write(self.channel, 'SETP %.3f' % value)
                time.sleep(1.0)
                #val = self.get_setpoint()
                break
            except:
                print('Problem with setting setpoint ')
                time.sleep(0.2)

    def set_SPramp(self, value, onoff):
        while True:
            try:
                self.sim900.clearbuf(self.channel)
                time.sleep(0.1)
                self.sim900.write(self.channel, 'RAMP %d' % onoff)
                time.sleep(1.0)
                self.sim900.write(self.channel, 'RATE %.6f' % value)
                time.sleep(1.0)
                break
            except:
                print('Problem setting setpoint-ramp-rate')
                time.sleep(0.2)

    def ramp_startstop(self, startstop):
        while True:
            try:
                self.sim900.clearbuf(self.channel)
                time.sleep(0.1)
                self.sim900.write(self.channel, 'STRT %d' % startstop)
                time.sleep(1.0)
                break
            except:
                print('Problem setting ramp start/stop')
                time.sleep(0.2)

    def get_outputval(self):
        while True:
            try:
                self.sim900.clearbuf(self.channel)
                time.sleep(0.1)
                self.sim900.write(self.channel, 'OMON?')
                time.sleep(0.1)
                val = self.sim900.getval(self.channel)
                break
            except:
                print('Problem getting output value')
                time.sleep(0.2)
        return val

    def set_manual_output(self, val):
        while True:
            try:
                self.sim900.clearbuf(self.channel)
                time.sleep(0.1)
                self.sim900.write(self.channel, 'MOUT %.6f' % val)
                time.sleep(0.1)
                break
            except:
                print('Problem setting manual output value')
                time.sleep(0.2)

    def set_to_manual(self):
        while True:
            try:
                self.sim900.clearbuf(self.channel)
                time.sleep(0.1)
                self.sim900.write(self.channel, 'AMAN 0')
                time.sleep(0.1)
                break
            except:
                print('Problem setting to manual')
                time.sleep(0.2)

    def set_to_PID(self):
        while True:
            try:
                self.sim900.clearbuf(self.channel)
                time.sleep(0.1)
                self.sim900.write(self.channel, 'AMAN 1')
                time.sleep(0.1)
                break
            except:
                print('Problem setting to PID')
                time.sleep(0.2)


if __name__ == '__main__':
    sim = device('dev2', 3)
    time.sleep(2)
    res = sim.get_setpoint()
    print(res)
