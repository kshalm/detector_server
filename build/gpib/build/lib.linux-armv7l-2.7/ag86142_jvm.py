from __future__ import division
from __future__ import print_function
from past.utils import old_div
from builtins import object
#!/usr/bin/env python
from Gpib import *
import time


class dev(object):
    def __init__(self, name):
        """Connect to ag86142B"""
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
        #self.meter.ibloc()
        self.meter.close()
        #self.meter.ibloc()


if (__name__ == '__main__'):
    if len(sys.argv) > 2:
        nrec = int(sys.argv[2])
    else:
        nrec = 300000
    filename = sys.argv[1]
    file = open(filename, 'w')
    dev1 = dev('dev5')
    dev1.write('trac:data:y? tra')
    a = dev1.read(65535)
    file.write('A, \n')
    file.write(a)
    #this is where the data is written
    file.flush()
    dev1.write('trac:data:x:start? tra')
    a = dev1.read(255)
    start = float(a)
    dev1.write('trac:data:x:stop? tra')
    a = dev1.read(255)
    stop = float(a)
    dev1.write('trac:poin? tra')
    a = dev1.read(255)
    numpoints = int(a)
    print(start, stop, numpoints - 1)
    df = old_div((stop - start), (numpoints - 1.0))
    #file.write('%f',start)
    f = start
    # file.write('START, \n');
    # file.print(start);
    #  file.write('STOP, \n');
    # file.write(stop);
    file.write('START, %e\n' % start)
    file.write('STOP, %e\n' % stop)
    file.write('LENGTH, %d\n' % numpoints)
    #  for c in range(numpoints):
    #    file.write('%e,' %f)
    #   print f
    #    f = f+df;
    file.write('\n')
    file.close()
    dev1.close()
