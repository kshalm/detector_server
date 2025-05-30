from __future__ import print_function
from builtins import str
#!/usr/bin/env python
import sys, os, string, time
#from Gpib import *
#import serial
import threading
import ag8166
from copy import deepcopy
import numpy as np
params = [
    {
        'name': 'AG81591A switch GPIB Address',
        'type': 'int',
        'limits': (1, 32),
        'value': 5
    },
    {
        'name': 'AG81591A slot',
        'type': 'int',
        'limits': (1, 20),
        'value': 1
    },
    #{'name':'AG81591A channel','type':'list','values':{'A':'A','B':'B'},'value':'A'},
]


class dev(ag8166.dev):
    def __init__(self, addr, serialport='', slot=2):  #,ch='A'):
        """ Written by SaeWoo and Jeff """
        ag8166.dev.__init__(self, addr, serialport)
        #print 'after call to super in %s, %d, %s'%(__name__, self.addr,self.port)
        #print self.addr
        if type(addr) == list:
            self.p = addr  # should I make a deepcopy here?  Not sure, will not for now
            for item in self.p:
                if 'value' in item:
                    name = item['name']
                    value = item['value']
                    if 'ddress' in name:
                        gpibaddress = value
                    elif 'slot' in name:
                        slot = value
                    #elif 'channel' in name:
                    #    ch = value
                    #print 'config from list addr %d, slot %d'%(gpibaddress, slot)
        elif type(addr) == str:
            # The arguments are shifted by 1
            gpibaddress = int(addr.strip('dev'))
            if type(serialport) == int:
                #ch = slot
                slot = serialport
        else:  # assuming addr is n integer..., using serial port
            gpibaddress = addr
        self.slot = slot
        self.gpibaddress = gpibaddress
        #self.ch = ch
        #print type(gpibaddress)
        params[0]['value'] = gpibaddress
        params[1]['value'] = self.slot
        #params[2]['value']=self.ch 
        if not hasattr(self, 'p'):
            self.p = deepcopy(params)

    def get_param(self, msgout):
        self.meter.write(msgout)
        reply = self.meter.read(100).strip()
        ret = float(reply.strip())
        return ret

    def set_param(self, msgout, msgcheck, value):
        self.meter.write(msgout)
        ret = self.get_param(msgcheck)
        if ret != value:
            print('problem with %s' % msgout)
            raise Exception('problem with %s' % msgout)
            ret = float('NaN')
        return ret

    def get_route(self):
        msgout = 'ROUT%d?' % (self.slot)
        self.meter.write(msgout)
        msgin = self.meter.read(100)
        msgparts = string.split(msgin.strip(), ',')
        return int(msgparts[1])

    def set_route(self, left, value):
        msgout = 'ROUT%d:CHAN %c,%d' % (self.slot, left, value)
        self.meter.write(msgout)
        ret = self.get_route()
        if ret != value:
            print('problem with %s' % msgout)
            raise Exception('problem with %s' % msgout)
            ret = float('NaN')
        return ret

    def route(self, value):
        return self.set_route('a', value)

    def identify(self):
        msg = '*IDN?'
        self.meter.write(msg)
        time.sleep(0.1)
        chassisid = self.meter.read().strip()
        """identify the module in a chosen slot"""
        slot = self.slot
        msg = ':SLOT%s:IDN?' % (str(slot))
        self.meter.write(msg)
        time.sleep(0.1)
        slotid = self.meter.read().strip()
        """identify the module in a chosen slot"""
        msg = ':ROUT%s?' % (str(slot))
        self.meter.write(msg)
        time.sleep(0.1)
        headid = self.meter.read().strip()

        return '# Chassis gpib %d: \t%s\n# Slot %d: \t\t%s\n# ROUT: \t\t%s\n' % (
            self.gpibaddress, chassisid, self.slot, slotid, headid)

    def writeconfig(self, f):
        msg = self.identify()
        #f.write('# Agilent 86142a in slot %d\n'%(self.slot))
        #f.write('#    ID: %s\n'%msg)
        f.write(msg)
        f.flush()

    def close(self):
        self.meter.close()

    def get_status(self):
        while True:
            self.meter.write('STAT%d:OPER?' % self.slot)
            msgin = self.meter.read(100)
            #print 'msgin: '+repr(msgin)
            if len(msgin) > 0:
                if msgin[-1] == '\n':
                    break
            time.sleep(1)
        self.status = int(msgin.strip())
        return self.status

    def loc(self):
        self.meter.loc()

    def set_lambda(self, wl):
        return


if __name__ == '__main__':
    meter = dev('dev9', 13)
    print(meter.get_route())
    print(meter.set_cont('A', 1))
    meter.meter.tmo()
