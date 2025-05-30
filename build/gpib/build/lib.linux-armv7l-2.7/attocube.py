from builtins import object
#!/usr/bin/env python
import sys, os, string, time
import serial
import threading


class device(object):
    def __init__(self, name):
        """Connect to attocube"""
        #print name

        self.device = serial.Serial(name, baudrate=38400, timeout=0.1)

    def write(self, msg):
        outstring = "%s\r\n" % (msg)
        self.device.write(outstring)
        #time.sleep(0.01)
        #msg = self.read()
        #print msg
    def read(self):
        msg = self.device.read(8000)
        #sys.stdout.write(msg)
        #sys.stdout.flush()
        return msg

    def close(self):
        self.device.close()

    def getm(self, axis):
        self.write('getm %d' % axis)
        msg = self.read()
        return msg

    def getf(self, axis):
        self.write('getf %d' % axis)
        msg = self.read()
        return msg

    def getc(self, axis):
        self.write('setm %d cap' % axis)
        m = self.read()
        time.sleep(1)
        self.write('getc %d' % axis)
        msg = self.read()
        #print msg
        self.write('setm %d gnd' % axis)
        m = self.read()
        #print m
        return msg

    def setf(self, axis, f):
        self.write('setf %d %d' % (axis, f))
        msg = self.read()
        return msg

    def setv(self, axis, v):
        self.write('setv %d %d' % (axis, v))
        msg = self.read()
        return msg

    def stepuslow(self, axis, size):
        self.write('setm %d stp' % axis)
        m = self.read()
        time.sleep(0.5)
        self.write('stepu %d %d' % (axis, size))
        m = self.read()
        time.sleep(0.5)
        self.write('setm %d gnd' % axis)
        m = self.read()

    def stepdslow(self, axis, size):
        self.write('setm %d stp' % axis)
        m = self.read()
        time.sleep(0.5)
        self.write('stepd %d %d' % (axis, size))
        m = self.read()
        time.sleep(0.5)
        self.write('setm %d gnd' % axis)
        m = self.read()


if __name__ == '__main__':
    attocube = device('COM4')
    #attocube.write('help')
    #msg = attocube.read()
    #msg = attocube.getc(3)
    #print msg+'\n'
    attocube.stepuslow(1, 5)
    attocube.stepdslow(1, 5)
    attocube.close()
