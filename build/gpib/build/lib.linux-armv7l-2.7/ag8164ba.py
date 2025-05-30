#!/usr/bin/env python
from __future__ import print_function
import sys, os, string, time
#from Gpib import *
#import serial
import threading
import ag81533a, ag8166
from copy import deepcopy

params = [
    {
        'name': 'AG81634A power meter GPIB Address',
        'type': 'int',
        'limits': (1, 32),
        'value': 11
    },
    {
        'name': 'AG81634A power meter slot',
        'type': 'int',
        'limits': (1, 20),
        'value': 4
    },
]


class dev(ag81533a.dev):
    def __init__(self, addr, serialport='', slot=4):
        ag81533a.dev.__init__(self, addr, serialport, slot)
        params[0]['value'] = self.gpibaddress
        params[1]['value'] = self.slot
        if not hasattr(self, 'p'):
            self.p = deepcopy(params)


#print params
if __name__ == '__main__':
    meter = dev('dev9', 11)
    #meter.set_lambda(1550)
    print(meter.get_lambda())
    import sys
    meter.writeconfig(sys.stdout)
