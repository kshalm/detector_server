from __future__ import print_function
from builtins import range
from builtins import object
#!/usr/bin/env python
from Gpib import *
import time


class dev(object):
    def __init__(self, name):
        """Connect to SR430"""
        self.meter = Gpib(name)
        meter = self.meter
        #self.reset()
        #meter.write('ZERO:AUTO OFF')
    def write(self, str):
        self.meter.write(str)

    def read(self, len):
        a = self.meter.read(len)
        return a

    def reset(self):
        """Reset the DMM and it's registers."""
        self.meter.write('*RST')
        self.meter.write('*CLS')

    def close(self):
        """End communication with the DMM"""
        self.meter.close()
        #self.meter.ibloc()


if (__name__ == '__main__'):
    if len(sys.argv) > 2:
        nrec = int(sys.argv[2])
    else:
        nrec = 300000
    filename = sys.argv[1]
    file = open(filename, 'w')
    dev1 = dev('dev8')
    while (1):
        dev1.write('SCAN?')
        a = dev1.read(14)
        print(a, end=' ')
        if (int(a) > nrec):
            break
        time.sleep(2)
    dev1.write('PAUS')
    dev1.write('BINA?')
    for c in range(1025):
        b = dev1.read(14)
        #print c,b
        file.write(b + '\n')
        file.flush()
    dev1.write('SCAN?')
    a = dev1.read(14)
    file.write(a + '\n')
    print(a, end=' ')
    file.close()
    dev1.close()
