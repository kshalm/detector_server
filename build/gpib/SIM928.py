#!/usr/bin/env python
from __future__ import print_function
import time
#from Gpib import *
#import serial
# import threading
import SIM900gpib
from copy import deepcopy

params = [
    {
        'name': 'Voltage Source GPIB Address',
        'type': 'int',
        'limits': (1, 32),
        'value': 4
    },
    {
        'name': 'Voltage Source Slot in SRS',
        'type': 'int',
        'values': {1, 2, 3, 4, 5, 6, 7, 8},
        'value': 3
    },
]


class dev(SIM900gpib.dev):
    def __init__(self, addr, serialport='', slot=0):
        # not sure why this command does not work
        #super(dev, self).__init__(self,addr,serialport)
        SIM900gpib.dev.__init__(self, addr, serialport)
        #print addr
        #print serialport
        #print slot
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
            print('config from list addr %d, slot %d' % (gpibaddress, slot))
        elif type(addr) == str:  # arguments are shifted by 1
            gpibaddress = int(addr.strip('dev'))
            if type(serialport) == int:
                slot = int(serialport)
        else:
            gpibaddress = addr
        self.addr = gpibaddress
        self.slot = slot
        params[0]['value'] = gpibaddress
        params[1]['value'] = slot
        if not hasattr(self, 'p'):
            self.p = deepcopy(params)

    def set_volt(self, volt):
        self.conn(self.slot)
        self.write('VOLT %.3f' % volt)
        self.write('xyz')

    def get_src_volt(self):
        a = 0
        while a < 3:
            #print a
            try:
                self.conn(self.slot)
                self.write('VOLT?')
                msgin = self.read()
                self.write('xyz')
                #print 'SIM928 get_src_volt',repr(msgin)
                return float(msgin)
                break
            except ValueError:
                a = a + 1

    def get_volt(self):
        return self.get_src_volt()

    def get_exon(self):
        self.conn(self.slot)
        self.write('EXON?')
        msgin = self.read()
        # print('EXON: %r'%repr(msgin))
        self.write('xyz')
        msgin = msgin.strip()
        if (msgin == 'ON') | (msgin == '1'):
            return True
        elif (msgin == 'OFF') | (msgin == '0'):
            return False
        else:
            raise ValueError

    def set_power_on(self):
        self.conn(self.slot)
        self.write('OPON')
        self.write('xyz')

    def set_power_off(self):
        self.conn(self.slot)
        self.write('OPOF')
        self.write('xyz')

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
        f.write('# SIM928 in slot %d: ' % (self.slot) + msg + '\n')
        f.flush()

    def close(self):
        self.meter.close()


if __name__ == '__main__':
    sim = dev(4, '/dev/ttyUSB0', 1)
    print(sim.identify().strip())
    print(sim.get_exon())
    #print msg
    #print 'A:',sim.getTempA()
