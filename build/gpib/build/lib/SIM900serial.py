from __future__ import print_function
from builtins import object
#!/usr/bin/env python
import sys, os, string, time
import serial
import threading


class dev(object):
    def __init__(self, serialport=''):
        """Connect to SIM900"""
        self.meter = serial.Serial(serialport, 115200, timeout=1)
        """   Stuff that is done for GPIB, not sure needed for serial... Need to figure out
    self.meter.write("*RST\r")
    self.meter.write('FLSH\r')
    #time.sleep(0.2)
    self.meter.write('SRST\r')
    #time.sleep(0.2)
    self.meter.write('CEOI ON\n')
    self.meter.write('CEOI?\n')
    msg = self.meter.read(3)    
    """

        self.meter.write("*IDN?\r")
        print('initializing SIM900')
        while True:
            msg = self.meter.readline()
            print('check identity of SIM900', repr(msg))
            if 'SIM900' in msg:
                break
            elif 'SIM' in msg:
                self.meter.write('xyz\r')
                self.meter.write('*IDN?\r')

    def conna(self):
        outstring = "CONN a, \"xyz\"\r"  #conna is a hard-wired connection to auxiliary port a.
        self.meter.write(outstring)

    def conn(self, slot):
        outstring = "CONN %d,\"xyz\"\r\n" % slot
        #print outstring
        self.meter.write(outstring)
        self.meter.write('\r\n')

    def openconn(self, slot):
        self.conn(slot)

    def closeconn(self, slot):
        outstring = "\"xyz\"\r"
        self.meter.write(outstring)

    def write(self, msg):
        outstring = "%s\r" % (msg)
        #print outstring
        ret = self.meter.write(outstring)
        time.sleep(0)
        return ret

    def read(self):
        data = self.meter.read()
        #print 'leng of message:%d\n'%len(data),
        #sys.stdout.write(data)
        #sys.stdout.flush()
        self.msg = data
        return data

    def readline(self):
        count = 0
        while True:
            data = self.meter.readline()
            if len(data) > 0:
                break
            print('no data, trying again')
            if count > 3:
                return float('Nan')
            time.sleep(0.01)
            count += 1
        self.msg = data
        return data

    def close(self):
        self.meter.close()


if __name__ == '__main__':

    sim = dev('/dev/ttyUSB1')
    #print msg
    #print 'A:',sim.getTempA()
    a = sim.conn(4)
    #time.sleep(1)
    while True:
        sim.write('RVAL?')
        #time.sleep(1)
        a = sim.readline()
        print(repr(a))
    sim.closeconn(4)
