from __future__ import print_function
from builtins import input
from builtins import object
import serial
import sys
import time
import numpy


class device(object):
    def __init__(self, name):
        self.device = serial.Serial(
            name,
            baudrate=9600,
            timeout=0.5,
            stopbits=1,
            parity='N',
            bytesize=8,
            xonxoff=1)

        print('Signing on')
        self.write(' ')  # sign on
        self.write('I500')
        self.write('V600')
        self.write('D1')
        self.write('Z')
        print('Setting origin')
        self.setOrigin()

    def write(self, msg):
        outstring = "%s\r" % (msg)
        self.device.write(outstring)
        msg = self.device.read(100)
        print('%d:%s' % (len(msg), msg))
        #time.sleep(0.5)

    def relativeWL(self, wl):
        step = -wl * 8
        outstring = '%+d' % (step)
        #print outstring
        self.write(outstring)

    def relative(self, wl):
        step = -wl
        outstring = '%+d' % (step)
        #print outstring
        self.write(outstring)

    def setOrigin(self):
        eval(input('Hit return when the monochromator is set to 0'))
        self.write('O0')

    def close(self):
        self.device.close()


if (__name__ == '__main__'):
    dev = device('COM2')
    print('Setting wavelength A')
    dev.relativeWL(100)
    dev.write('Z')
    #print 'Setting wavelength B'
    dev.close()
