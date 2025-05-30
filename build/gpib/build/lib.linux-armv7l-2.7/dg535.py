from builtins import object
#!/usr/bin/env python
from Gpib import *


class dev(object):
    def __init__(self, name):
        """Connect to and reset a DG535"""
        self.meter = Gpib(name)
        meter = self.meter
        #self.reset()
        #meter.write('ZERO:AUTO OFF')
    def write(self, str):
        self.meter.write(str)

    def reset(self):
        """Reset the DMM and it's registers."""
        self.meter.write('*RST')
        self.meter.write('*CLS')

    def close(self):
        """End communication with the DMM"""
        self.meter.close()


if (__name__ == '__main__'):
    dev1 = dev('dev14')
    dev1.write('DT 2,1,100e-9')
    dev1.close()
