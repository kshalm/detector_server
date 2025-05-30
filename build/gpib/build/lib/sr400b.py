from __future__ import print_function
from builtins import range
from builtins import object
#!/usr/bin/env python
from Gpib import *
import time


class dev(object):
    def __init__(self, name):
        """Connect to SR400"""
        self.meter = Gpib(name)
        meter = self.meter
        #self.reset()
        #meter.write('ZERO:AUTO OFF')
    def write(self, str):
        self.meter.write(str)

    def read(self):
        a = self.meter.read(100)
        return int(a)

    def reset(self):
        """Reset the DMM and it's registers."""
        self.meter.write('*RST')
        self.meter.write('*CLS')

    def close(self):
        """End communication with the DMM"""
        self.meter.close()


if (__name__ == '__main__'):
    filename = sys.argv[1]
    file = open(filename, 'w')
    dev1 = dev('dev5')
    dev1.write('SD 1')
    counter = 1
    nperiods = 2000
    str = "NP %d" % nperiods
    dev1.write(str)
    while (1):
        print("Takeing buffer %d" % (counter), end=' ')
        dev1.write('CR')
        dev1.write('CS')
        while (1):
            time.sleep(1)
            dev1.write('NN')
            a = dev1.read()
            if (a == nperiods):
                break
        dev1.write('ET')
        print("reading %d" % counter)
        for c in range(nperiods):
            a = dev1.read()
            b = dev1.read()
            str = '%d\t%d' % (a, b)
            #print "%d\t"%(c)+str
            file.write(str + '\n')
        file.flush()
        print(str)
        counter = counter + 1
    dev1.close()
