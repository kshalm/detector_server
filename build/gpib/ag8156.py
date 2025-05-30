from __future__ import print_function
from builtins import str
from builtins import object
#!/usr/bin/env python
import Gpib
from copy import deepcopy

params = [
    {
        'name': 'address',
        'type': 'int',
        'value': 4,
        'limits': (1, 32)
    },
    {
        'name': 'Wavelength',
        'type': 'float',
        'limits': (1000, 2000),
        'value': 1550.0
    },
    {
        'name': 'Attenuation',
        'type': 'float',
        'limits': (0, 60),
        'value': 50.06
    },
]


class dev(object):
    def __init__(self, addr, serialport=''):
        """Connect to and reset an agilent 8156A"""

        # -- Add general declaration 3/3/2015 --
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        # -- end --

        if type(addr) == str:
            gpibaddress = int(addr.strip('dev'))
            self.meter = Gpib.Gpib(addr)
        else:
            gpibaddress = addr
            self.meter = Gpib.Gpib(addr, serialport)
        """Connect to and reset a HP35131A"""
        self.p = deepcopy(params)
        self.addr = gpibaddress

    def set_att(self, att):
        """Set the attenuation"""
        msg = 'INP:ATT %s' % (str(att))
        self.meter.write(msg)

    def set_lambda(self, wav):
        """Set the wavelength in nm"""
        msg = ':INP:WAV %snm' % (str(wav))
        self.meter.write(msg)

    def get_lambda(self):
        """Get the attenuation"""
        try:
            self.meter.write(':INP:WAV?')
            reading = self.meter.read()
            return float(reading)
        except self.meter.error:
            return None

    def get_att(self):
        """Get the attenuation"""
        try:
            self.meter.write('INP:ATT?')
            reading = self.meter.read()
            return float(reading)
        except self.meter.error:
            return None

    def reset(self):
        """Reset the DMM and it's registers."""
        self.meter.write('*RST')
        self.meter.write('*CLS')

    def enable(self):
        self.meter.write('OUTP ON')

    def disable(self):
        self.meter.write('OUTP OFF')

    def identify(self):
        msg = '*IDN?'
        self.meter.write(msg)
        result = self.meter.read()
        return result

    def writeconfig(self, f):
        msg = self.identify().strip()
        f.write('# 8156 is %s\n' % (msg))
        f.write('# 8156 lambda is %s\n' % (self.get_lambda()))
        f.write('# 8156 attenuation is %s\n' % (self.get_att()))
        f.flush()

    def close(self):
        """End communication with the DMM"""
        self.meter.close()

    def get_params_from_inst(self):
        """ Read settings from the instrument and load them in the params varialbe """
        for item in self.p:
            if 'value' in item:
                print(item['name'], item['value'])
            if item['name'] == 'Wavelength':
                item['value'] = float(self.get_lambda())
            elif item['name'] == 'Attenuation':
                item['value'] = float(self.get_att())
            if 'value' in item:
                print(item['value'])


if (__name__ == '__main__'):
    dev1 = dev('dev8')
    a = dev1.enable()
    dev1.set_att(0)
    dev1.close()
