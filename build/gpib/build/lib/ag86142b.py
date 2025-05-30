#!/usr/bin/env python
# modified
from __future__ import division
from builtins import range
from builtins import object
from past.utils import old_div
from Gpib import *
import time
import ctypes
import string
import numpy


class dev(object):
    def __init__(self, name):
        """Connect to and reset an agilent 8166A"""
        self.meter = Gpib(name)
        meter = self.meter
        self.meter.write('SYST:COMM:GPIB:BUFF ON')
        self.meter.write('INIT:CONT OFF')
        #self.meter.write('*ESE 0')
        #self.reset()
        #meter.write('ZERO:AUTO OFF')
    def set_start(self, wav):
        msg = 'SENS:WAV:STAR %.3fnm' % wav
        self.meter.write(msg)

    def set_stop(self, wav):
        msg = 'SENS:WAV:STOP %.3fnm' % wav
        self.meter.write(msg)

    def set_center(self, wav):
        msg = 'SENS:WAV:CENT %.3fnm' % wav
        self.meter.write(msg)

    def set_span(self, wav):
        msg = 'SENS:WAV:SPAN %.3fnm' % wav
        self.meter.write(msg)

    def get(self, msg):
        self.meter.write(msg)
        ret = self.meter.read(50)
        ret = string.split(ret, '\n')
        return float(ret[0])

    def get_start(self):
        msg = 'SENS:WAV:START?'
        return self.get(msg)

    def get_stop(self):
        msg = 'SENS:WAV:STOP?'
        return self.get(msg)

    def get_span(self):
        msg = 'SENS:WAV:SPAN?'
        return self.get(msg)

    def get_center(self):
        msg = 'SENS:WAV:CENT?'
        return self.get(msg)

    def get_numpoints(self):
        msg = 'SENS:SWE:POIN?'
        return self.get(msg)

    def single_trigger(self):
        msg = 'INIT;*OPC'
        self.meter.write(msg)
        #msg = '*OPC'
        #self.meter.write(msg);
    def get_traceA(self):
        msg = 'TRAC? TRA'
        self.meter.write(msg)
        c = self.meter.read(1)
        #print c
        m_len = self.meter.read(1)
        m_len = int(m_len)
        #print m_len 
        msg_len = self.meter.read(m_len)
        msg_len = int(msg_len)
        #print msg_len
        msg = self.meter.readbinary(msg_len + 1)
        #print len(msg)
        msg = msg[0:msg_len]
        data = numpy.fromstring(msg, dtype='Float64')
        data = data.newbyteorder()
        return data

    def get_Xaxis(self):
        start = self.get_start()
        stop = self.get_stop()
        span = self.get_span()
        numpoints = self.get_numpoints()
        step = old_div((stop - start), (numpoints - 1.0))
        wavelength = numpy.arange(start, stop + step, step)
        return wavelength

    def save_traceA(self, fname):
        data = self.get_traceA()
        wavelength = self.get_Xaxis()
        fp = open(fname, 'w')
        for i in range(len(data)):
            msg = '%.8e\t%.8f\n' % (wavelength[i], data[i])
            fp.write(msg)
            fp.flush()
        fp.close()

    def reset(self):
        """Reset the DMM and it's registers."""
        self.meter.write('*RST')
        self.meter.write('*CLS')

    def close(self):
        """End communication with the DMM"""
        self.meter.close()


if (__name__ == '__main__'):
    dev1 = dev('dev13')
    #f = open('test.dat','wb');
    dev1.single_trigger()
    dev1.save_traceA('test.dat')
    dev1.close()
