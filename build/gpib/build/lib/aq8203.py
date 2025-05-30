from __future__ import print_function
from builtins import object
#!/usr/bin/env python
from Gpib import *
import string, time


class dev(object):
    def __init__(self, name):
        """Connect """
        self.meter = Gpib(name)

    def set_att(self, att):
        """Set the attenuation"""
        self.meter.write('C1')
        msg = 'LATL%.2f' % att
        self.meter.write(msg)

    def set_lambda(self, wav):
        """Set the wavelength in nm"""
        self.meter.write('C1')
        msg = 'LW%.2f' % wav
        print(msg)
        self.meter.write(msg)

    def set_power(self, pow):
        self.meter.write('C1')
        msg = 'LPL%.2f' % pow
        print(msg)
        self.meter.write(msg)

    def turn_on(self):
        self.meter.write('C1')
        msg = 'LOPT1'
        self.meter.write(msg)

    def turn_off(self):
        self.meter.write('C1')
        msg = 'LOPT0'
        seof.meter.write(msg)

    def get_lambda(self):
        """Get the wavelength"""
        try:
            msg = 'LW?'
            self.meter.write('C1')
            self.meter.write(msg)
            reading = self.meter.read()
            print(reading)
            return reading
        except self.meter.error:
            return None


if (__name__ == '__main__'):
    dev1 = dev('dev12')
    dev1.set_lambda(1515.1)
    #time.sleep(10)
    a = dev1.get_lambda()
    print(a)
    dev1.turn_on
    time.sleep(10)
    dev1.turn_off
