from __future__ import print_function
from builtins import range
#!/usr/bin/env python
import sys, os, string, time
#from Gpib import *
#import serial
import threading
import SIM900gpib
from copy import deepcopy

params = [
    {
        'name': 'Voltage meter GPIB Address',
        'type': 'int',
        'limits': (1, 32),
        'value': 4
    },
    {
        'name': 'Voltage meter Slot in SRS',
        'type': 'int',
        'values': {1, 2, 3, 4, 5, 6, 7, 8},
        'value': 7
    },
    {
        'name': 'Voltage meter number in SRS',
        'type': 'int',
        'values': {1, 2, 3, 4},
        'value': 1
    },
]


class dev(SIM900gpib.dev):
    def __init__(self, addr, serialport='', slot=0, ch=0):
        SIM900gpib.dev.__init__(self, addr, serialport)
        if type(addr) == list:
            self.p = addr  # should I make a deepcopy here?  Not sure, will not for now
            for item in self.p:
                if 'value' in item:
                    name = item['name']
                    value = item['value']
                    if 'ddress' in name:
                        gpibaddress = value
                    elif 'Slot' in name:
                        slot = value
                    elif 'meter number' in name:
                        ch = value
            print('config from list addr %d, slot %d, ch %d' %
                  (gpibaddress, slot, ch))
        elif type(addr) == str:  # Arguments are shifted by 1
            gpibaddress = int(addr.strip('dev'))
            if type(serialport) == int:
                ch = slot
                slot = serialport
                print('slot: %d, ch%d' % (slot, ch))
        else:
            gpibaddress = addr
        self.ch = ch
        self.slot = slot
        self.addr = gpibaddress
        params[0]['value'] = gpibaddress
        params[1]['value'] = slot
        params[2]['value'] = ch
        if not hasattr(
                self, 'p'
        ):  # create attribute p because class was instantiated w/o list
            self.p = deepcopy(params)

    def getReadings(self):
        self.conn(self.slot)
        self.write('VOLT? 0')
        msgin = self.read()
        self.write('xyz')
        try:
            readings = msgin.strip().split(',')
            for i in range(len(readings)):
                readings[i] = float(readings[i])
        except:
            readings = []
        return readings

    def get_dvm_volt(self):
        a = 0
        while a < 3:
            #print a
            try:
                self.conn(self.slot)
                self.write('VOLT? %d' % self.ch)
                msgin = self.read()
                self.write('xyz')
                return float(msgin)
                break
            except ValueError:
                a = a + 1

    def get_volt(self):
        return self.get_dvm_volt()

    def identify(self):
        self.conn(self.slot)
        msg = '*IDN?'
        self.write(msg)
        time.sleep(0.1)
        ret = self.read()
        #print repr(ret)
        self.write('xyz')
        return ret

    def writeconfig(self, f):
        msg = self.identify().strip()
        f.write('# SIM970 in slot %d,channel %d: ' % (self.slot, self.ch) + msg
                + '\n')
        f.flush()

    def close(self):
        self.meter.close()


if __name__ == '__main__':
    sim = dev('dev13', slot=7, ch=2)
    #print msg
    #print 'A:',sim.getTempA()
    #a = sim.conn(7)
    #sim.write('VOLT? 2')
    #a = sim.read();
    #print a
    #sim.write('xyz')
    print(sim.get_dvm_volt())
