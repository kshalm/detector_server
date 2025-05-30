from __future__ import print_function
import base_optical_attenuator
import Gpib
import numpy as np

import time
import ctypes
import string

# useless comment

params = [
    {
        'name': 'AQ8233 GPIB Address',
        'type': 'int',
        'limits': (1, 32),
        'value': 4
    },
    {
        'name': 'AQ8233 Slot',
        'type': 'int',
        'values': {1, 2, 3},
        'value': 3
    },
]


class dev(base_optical_attenuator.dev):
    def __init__(self, addr, serialport='', slot=1):
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        meter = self.meter
        #  fill in correct values for params, and make a copy of this instance
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
            print('config from list addr %d, slot %d, ch %d' %
                  (gpibaddress, slot, ch))
        elif type(addr) == str:  # Arguments are shifted by 1
            gpibaddress = int(addr.strip('dev'))
            if type(serialport) == int:
                slot = serialport

        else:
            gpibaddress = addr
        self.slot = slot
        self.addr = gpibaddress
        params[0]['value'] = gpibaddress
        params[1]['value'] = slot
        if not hasattr(
                self, 'p'
        ):  # create attribute p because class was instantiated w/o list
            self.p = deepcopy(params)

    def identify(self):
        chassisid = super(dev, self).identify()
        self.meter.write('C%d' % self.slot)
        slotid = self.meter.query('MOD?', 0.1).strip()
        return '# Chassis gpib %d: \t%s\n# Slot %d: \t\t%s\n' % (
            self.addr, chassisid, self.slot, slotid)

    def writeconfig(self, fp):
        super(dev, self).writeconfig(fp)
        msgin = self.meter.query('MODEL?')
        fp.write('#  MODEL?: %s\n' % msgin.strip())
        msgin = self.meter.query('AD?')
        fp.write('#  AD?: %s\n' % msgin.strip())
        fp.flush()

    def get_att(self):
        loop = 0
        while loop < 3:
            self.meter.write('C%d' % self.slot)
            msg = self.meter.query('AAV?')
            msg = msg.strip()
            if len(msg) > 0:
                self.att = float(msg.strip().lstrip('AAV'))
                return self.att
            else:
                loop += 1
        print('Problem getting attenuator value')
        self.att = -1
        return self.att
        """
        self.meter.write('C%d\n'%self.slot)
        msg = self.meter.query('AAV?\n')
        if msg == '':
          while cnt < 5 and msg == '':
           msg = self.meter.read(100)
           print "multiple attempt msg: ", msg
           print "current cnt: ", cnt
           cnt += 1
           time.sleep(0.5)
        if cnt == 5 and msg =='':
          print "could not get attn reading"
          msg = 'AAV999999\r\n'
        print "Final msg: ", msg
        self.att = float(msg.strip().lstrip('AAV'))
        return self.att 
            """

    def set_att(self, value):
        self.meter.write('C%d\n' % self.slot)
        value = np.abs(value)
        self.meter.write('AAV%.3f\n' % (value))
        if value != self.get_att():
            print('Problem setting attenuator to %.3f, gpib: %d, slot: %d' %
                  (value, self.addr, self.slot))
        return self.att

    def get_lambda(self):
        self.meter.write('C%d\n' % self.slot)
        msg = self.meter.query('AW?\n')
        #print 'Msg from query',msg
        if len(msg) > 2:
            self.wl = float(msg.strip().lstrip('AW'))
            return self.wl
        else:
            return float('nan')

    def set_lambda(self, value):
        self.meter.write('C%d\n' % self.slot)
        value = int(value)
        self.meter.write('AW%d\n' % int(value))
        wl = self.get_lambda()
        if value != wl:
            print(
                'Problem setting wavelength on the attenuator to %d, gpib: %d, slot: %d got: %f'
                % (value, self.addr, self.slot, wl))
        return None

    def enable(self):
        self.meter.write('C%d\n' % self.slot)
        self.meter.write('ASHTR1\n')
        return None

    def disable(self):
        self.meter.write('C%d\n' % self.slot)
        self.meter.write('ASHTR0\n')
        return None


if __name__ == '__main__':
    #att = dev(7,'COM8',1)
    att = dev(3, '/dev/ttyUSB0', 4)
    print(att.get_lambda())
    """
    import sys
    #att.enable()
    #att.set_att(11)
    #print att.meter.query('ASHTR?')
    print repr(att.identify())
    att.writeconfig(sys.stdout)
    #att.disable()
    """
