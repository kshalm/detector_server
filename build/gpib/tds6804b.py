from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import range
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import object
#!/usr/bin/env python
from Gpib import *
import time
import ctypes


class dev(object):
    def __init__(self, name):
        """Connect to and reset an agilent 8166A"""
        self.meter = Gpib(name)
        meter = self.meter
        #self.reset()
        #meter.write('ZERO:AUTO OFF')

    def run(self):
        self.meter.write('ACQ:STOPAfter SEQ')
        self.meter.write('ACQ:STATE ON')

    def stop(self):
        self.meter.write('ACQ:STATE OFF')

    def single(self):
        self.meter.write('ACQ:STOPAfter SEQ')
        self.meter.write('ACQ:STATE ON')

    def checkstate(self):
        self.meter.write('ACQ:STATE?')
        return (int(self.meter.read()))

    def qonchannel(self):
        self.meter.write('SELECT?')
        msg = self.meter.read()
        chlist0 = ['CH1','CH2','CH3','CH4','MATH1','MATH2','MATH3','MATH4',\
                             'REF1','REF2','REF3','REF4','CTR']
        onchlist = []
        for m in range(12):
            if msg[2 * m] == '1':
                onchlist = onchlist + [chlist0[m]]
        return (onchlist)

    def savewfm(self, ch, fn):
        # format of fn: <drive>/<dir>/<filename> or <filename>
        self.meter.write('SAVE:WAVEFORM %s,\"%s\"' % (ch, fn))

    def close(self):
        """End communication with the DMM"""
        self.meter.close()


if (__name__ == '__main__'):
    dev1 = dev('dev3')
    print('Checking live channels.')
    print(dev1.qonchannel())
    print('Stop.')
    dev1.stop()
    time.sleep(1)
    print('Single.')
    dev1.single()
    print('State?')
    while (dev1.checkstate() != 0):
        print('not done...')
        time.sleep(0.05)
    print('Saving waveform...')
    dev1.savewfm('CH2', 'test.wfm')

    dev1.close()
