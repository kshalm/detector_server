from __future__ import print_function
from builtins import str
#!/usr/bin/env python
import sys, os, string, time
#from Gpib import *
#import serial
import threading
import ag8166
from copy import deepcopy

params = [
    {
        'name': 'AG81980A Laser GPIB Address',
        'type': 'int',
        'limits': (1, 32),
        'value': 10
    },
    {
        'name': 'AG81980A slot',
        'type': 'int',
        'limits': (1, 20),
        'value': 1
    },
    {
        'name': 'Coherence Level (0=off)',
        'type': 'int',
        'value': 1,
        'limits': (0, 100)
    },
]


class dev(ag8166.dev):
    def __init__(self, addr, serialport='', slot=2):
        """ Written by SaeWoo and Jeff """
        # not sure why this command does not work
        super(dev, self).__init__(addr, serialport)
        # ahhhhhh:  dev in ag8166 needs to inherit from ojbect (i.e. class dev(object) in ag8166.py)
        #print type(dev)
        #print type(self)
        #ag8166.dev.__init__(self,addr,serialport)
        #print 'after call to super in ag81980',self.addr,self.port
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
            #print 'config from list addr %d, slot %d'%(gpibaddress, slot)
        elif type(addr) == str:
            # The arguments are shifted by 1
            gpibaddress = int(addr.strip('dev'))
            if type(serialport) == int:
                slot = serialport
        else:
            gpibaddress = addr
        self.slot = slot
        self.gpibaddress = gpibaddress
        #print type(gpibaddress)
        params[0]['value'] = gpibaddress
        params[1]['value'] = self.slot
        if not hasattr(self, 'p'):
            self.p = deepcopy(params)

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

    def set_am_state(self, level):
        msg1 = ':SOUR%d:AM:STAT %f' % (self.slot, level)
        msg2 = ':SOUR%d:AM:STAT?' % (self.slot)
        return self.set_param(msg1, msg2, level)

    def get_am_state(self):
        return self.get_param(':SOUR%d:AM:STAT?' % self.slot)

    def set_am_source(self, source):
        msg1 = ':SOUR%d:AM:SOUR %d' % (self.slot, source)
        msg2 = ':SOUR%d:AM:SOUR?' % (self.slot)
        return self.set_param(msg1, msg2, source)

    def get_am_source(self):
        return self.get_param(':SOUR%d:AM:SOUR?' % self.slot)

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

        return '# Chassis gpib %d: \t%s\n# Slot %d: \t\t%s\n' % (
            self.gpibaddress, chassisid, self.slot, slotid)

    #def identify(self):
    #  return self.identify_slot(self.slot)
    def writeconfig(self, f):
        msg = self.identify()
        wl = self.get_lambda()
        power = self.get_power()
        f.write(msg)
        f.write('# wavelength: %e\n# power: %f\n' % (wl, power))
        am_source = self.get_am_source()
        am_state = self.get_am_state()
        f.write('# AM modulation source: %d\n# AM state: %.2f\n' %
                (am_source, am_state))
        f.flush()

    def close(self):
        self.meter.close()


if __name__ == '__main__':
    #laser = dev('dev10',1)
    laser = dev(15, 'COM11', 0)
    print(laser.get_lambda())
    print(laser.get_power())
    #print laser.set_cohl(1)
    #print laser.get_cohl
    #print laser.set_power(0.004)
    print(laser.identify())
    import sys
    laser.writeconfig(sys.stdout)
