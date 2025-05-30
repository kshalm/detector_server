from __future__ import print_function
from builtins import str
from builtins import object
#import serial
import Gpib
import string

#import Gpib_prologix_nt_ver2 as Gpib


class dev(object):
    def __init__(self, addr, serialport=''):
        """Connect to and reset a Keithley485"""
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        self.meter.write('F0X\r\n')
        self.meter.write('R0X\r\n')

    def get_ammeter_current(self):
        #msg = 'G1X\r\n'
        #self.meter.write(msg)
        msgout = self.meter.read(100)
        #print repr(msgout)
        if len(msgout) == 0:
            print('Got empty string')
            msgout = 'NaN'
        #return float(msgout)
        x = float(msgout.strip('\r\nNDCA'))

        return x

    def auto_range(self):
        self.meter.write('R0X\r\n')
        #return map(float,msgout.split('\n')[1:2])[0]
    def get_current(self):
        return self.get_ammeter_current()

    def identify(self):
        identity = 'Keithley199 dmm; addr: ' + str(self.addr)
        return identity

    def writeconfig(self, f):
        msg = self.identify().strip()
        f.write('# ' + msg + '\n')
        f.flush()

    def close(self):
        self.meter.write('F0X\r\n')
        self.meter.close()


if (__name__ == '__main__'):
    import serial
    # serialport = serial.Serial('/dev/ttyUSB0', 9600, timeout = 0.5)
    # source = device(9,serialport)
    # source.meter.write('++addr')
    # print source.port.read()
    #dmm = device('dev8')
    dmm = dev(3, 'COM7')
    x = dmm.get_current()
    print(x)
    #fileName = '/Users/lab/Downloads/xxx'
    #f = open(fileName, 'w')
    #dmm.writeconfig(f)
