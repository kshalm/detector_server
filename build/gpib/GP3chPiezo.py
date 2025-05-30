from __future__ import print_function
from builtins import object
import serial


class device(object):
    def __init__(self, name):
        self.device = serial.Serial(
            name,
            baudrate=4800,
            timeout=0.5,
            stopbits=1,
            parity='N',
            bytesize=8,
            xonxoff=1)

    def setv(self, ch, v):
        outstring = 'CH%d %05.1f\r' % (ch, v)
        self.device.write(outstring)
        #print outstring

        msg = self.device.read(100)
        return msg
        #print msg

    def close(self):
        self.device.close()


if (__name__ == '__main__'):
    dev = device('COM13')
    v = [30, 30, 30]
    print('Setting voltages: %d %d %d' % (v[0], v[1], v[2]))
    dev.setv(1, v[0])
    dev.setv(2, v[1])
    dev.setv(3, v[2])

    dev.close()
