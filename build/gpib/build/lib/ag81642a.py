from __future__ import print_function
from builtins import str
#!/usr/bin/env python
import sys, os, string, time
#from Gpib import *
#import serial
import threading
import ag8166
from copy import deepcopy

params = [{
    'name': 'AG81642A laser GPIB Address',
    'type': 'int',
    'limits': (1, 32),
    'value': 11
}, ]


class dev(ag8166.dev):
    def __init__(self, addr, serialport=''):
        """ Written by SaeWoo and Jeff """
        ag8166.dev.__init__(self, addr, serialport)
        if type(addr) == str:
            gpibaddress = int(addr.strip('dev'))
        else:
            gpibaddress = addr
        self.slot = 0
        params[0]['value'] = gpibaddress
        self.p = deepcopy(params)

    def get_lambda(self):
        return self.get_source_lambda(self.slot)

    def identify(self):
        return self.identify_slot(self.slot)

    def get_param(self, msgout):
        self.meter.write(msgout)
        reply = self.meter.read(100).strip()
        try:
            ret = float(reply.strip())
        except:
            errmsg = 'problem with float conversion in %s, %s' % (
                msgout, reply.strip())
            print(errmsg)
            raise Exception(errmsg)
            ret = float('NaN')
        return ret

    def set_param(self, msgout, msgcheck, value):
        self.meter.write(msgout)
        ret = self.get_param(msgcheck)
        if ret != value:
            print('problem with %s' % msgout)
            raise Exception('problem with %s' % msgout)
            ret = float('NaN')
        return ret

    def enable(self):
        msg1 = 'OUTP%d:STAT 1' % (self.slot)
        msg2 = 'OUTP%d:STAT?' % (self.slot)
        return self.set_param(msg1, msg2, 1)

    def disable(self):
        msg1 = 'OUTP%d:STAT 0' % (self.slot)
        msg2 = 'OUTP%d:STAT?' % (self.slot)
        return self.set_param(msg1, msg2, 0)

    def get_lambda(self):
        try:
            msg = ':SOUR%s:WAV?' % (str(self.slot))
            self.meter.write(msg)
            self.wl = float(self.meter.read().strip())
            return self.wl
        except:
            return float('NaN')

    def set_lambda(self, wl):
        #try:
        msg = ':SOUR%d:WAV %fE-9' % (self.slot, wl)
        self.meter.write(msg)
        self.wl = self.get_lambda() * 1e9
        return self.wl

    #except:
    #  return float('NaN') 

    def get_power(self):
        try:
            msg = ':SOUR%s:POW?' % (str(self.slot))
            self.meter.write(msg)
            self.power = float(self.meter.read().strip())
            return self.power
        except:
            return float('NaN')

    def set_power(self, value):
        try:
            msg = ':SOUR%d:POW %f' % (self.slot, value)
            self.meter.write(msg)
            self.power = self.get_power()
            if value != self.power:
                print('Problem setting laser power to %f' % (value))
                self.power = float('NaN')
            return self.power
        except:
            return float('NaN')

    def set_cohl(self, level):
        if level > 0:
            self.set_am_source(1)
        else:
            self.set_am_source(0)

#      msg1=':SOUR%d:AM:COHC:COHL %f'%(self.slot, level)
#      msg2=':SOUR%d:AM:COHC:COHL?'%(self.slot)
#      return self.set_param(msg1,msg2,level)

    def get_cohl(self):
        #return self.get_param(':SOUR%d:AM:COHC:COHL?'%self.slot)
        return self.get_am_source()

    def set_am_source(self, source):
        msg1 = ':SOUR%d:AM:SOUR %d' % (self.slot, source)
        msg2 = ':SOUR%d:AM:SOUR?' % (self.slot)
        return self.set_param(msg1, msg2, source)

    def get_am_source(self):
        return self.get_param(':SOUR%d:AM:SOUR?' % self.slot)

    def writeconfig(self, f):
        msg = self.identify().strip()
        f.write('# Agilent 86142a in slot %d\n' % (self.slot))
        f.write('#    ID: %s\n' % msg)
        am_source = self.get_am_source()
        #cohl = self.get_cohl()
        #f.write('# AM modulation source: %d\n# Coherence level: %.2f\n'%(am_source,cohl))
        f.write('# AM modulation source: %d\n' % (am_source))
        f.flush()

    def close(self):
        self.meter.close()

if __name__ == '__main__':
    laser = dev('dev10', 0)
    print(laser.get_lambda())
    print(laser.get_am_source())
    import sys
    laser.writeconfig(sys.stdout)
