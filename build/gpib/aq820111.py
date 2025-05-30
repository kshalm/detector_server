from __future__ import print_function
import aq8201110
import Gpib
import threading
import time
import string
import numpy as np
import math

params = [
    {
        'name': 'AQ8201-110 GPIB Address',
        'type': 'int',
        'limits': (1, 32),
        'value': 4
    },
    {
        'name': 'AQ8201-110 Slot',
        'type': 'int',
        'values': {1, 2, 3, 5, 6, 7, 8, 9, 10},
        'value': 3
    },
]


class dev(aq8201110.dev):
    def set_lambda(self, value):
        loop = 0
        if value < self.wlmin:
            value = self.wlmin
        if value > self.wlmax:
            value = self.wlmax
        while loop < 3:
            self.meter.write('C%d' % self.slot)
            value = int(value)
            self.meter.write('LW%.3f' % float(value))
            self.wl = self.get_lambda()
            if value != self.wl:
                loop += 1
            else:
                return 0
        print(
            'Problem setting wavelength on the laser to %d, gpib: %d, slot: %d got:%f'
            % (value, self.addr, self.slot, self.wl))
        return -1


if __name__ == '__main__':
    #laser = dev('dev3',1)
    laser = dev(6, '/dev/ttyUSB0', 4)
    print(laser.identify().strip())
    #laser.set_power(1e-3)
    #print pm.zero()
    print('get lambda')
    print(laser.get_lambda())
    import sys
    laser.writeconfig(sys.stdout)
    print('try to disable')
    laser.disable()
    #print 'get status'
    #print laser.get_status()
    #laser.set_cohl(1)
    print(laser.get_lambda())
    laser.close()
