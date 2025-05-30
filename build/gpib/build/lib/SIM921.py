from __future__ import print_function
from builtins import object
#!/usr/bin/env python
import sys, os, string, time
import threading
from Gpib import *
import SIM900


class device(object):
    def __init__(self, name, channel):
        """Connect to SIM921"""
        self.sim900 = SIM900.device(name)
        self.channel = channel

    def getres(self):
        while True:
            try:
                self.sim900.write(self.channel, 'RVAL?')
                time.sleep(0.05)
                val = self.sim900.getval(self.channel)
                #print val
                val = float(val)
                break
            except:
                print('Problem with getting rval ')
                time.sleep(0.01)
        return val


if __name__ == '__main__':
    sim = device('dev2', 1)
    res = sim.getres()
    print(res)
