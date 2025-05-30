from __future__ import print_function
from builtins import object
#!/usr/bin/env python
import serial
import Gpib_prologix_nt_ver2 as Gpib
import time


class device(object):
    def __init__(self, addr, serialport=''):
        '''Connect to Antritsu MG96378'''

        # -- Add general declaration 3/3/2015 --
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        # -- end --

        #self.port = serialport
        #self.add = addr
        #self.meter = Gpib.Gpib(addr, serialport)
        meter = self.meter

    def setModeCW(self):
        self.meter.write('MCW')

    def setWavelength(self, wavelength):
        str = 'WCNT %.3fnm ' % wavelength
        self.meter.write(str)
        time.sleep(0.5)

    def setPower(self, power):
        str = 'POW %.3fmW' % power
        self.meter.write(str)
        time.sleep(0.5)

    def getWavelength(self):
        self.meter.write('OUTW?')
        return (float(self.meter.read()) * 1e9)

    def close(self):
        """End communication with the DMM"""
        self.meter.loc()


if (__name__ == '__main__'):
    port = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
    dev1 = device(12, port)
    dev1.setModeCW()
    dev1.setWavelength(1541.123)
    print(dev1.getWavelength())
    dev1.close()
