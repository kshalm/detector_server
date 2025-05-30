#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
from builtins import object
from past.utils import old_div
import sys, os, serial, string


class pyvbox(object):
    def __init__(self, port=0, baud=9600, address=0):

        if (port < 0 or port > 7):
            print('Error - Bad port number %d\n' % (port))
            return None

        baudlist = [300, 1200, 2400, 4800, 9600, 19200, 38400]

        if baud not in baudlist:
            print('Error - Unsupported baud rate: %d\n' % (baud))
            return None

        if (address < 0 or address > 15):
            print('Error - Bad address %d\n' % (address))
            return None
        self.address = address

        self.ser = serial.Serial()  #(0,baud)
        self.ser.port = "COM%d" % port
        self.ser.baudrate = baud
        self.voltage = None
        #self.ser.open()    
    def set(self, volt):
        if (volt < 0 or volt > 6.5535): return None
        self.voltage = volt

        # 1 bit = 100 uV
        val = int(volt * 10000.0 + 0.5)

        #     word0  high6bit 00
        #     word1  mid6bit 01
        #     word2  low4bit 10
        #     word3  address 11   -  address is 4 bits

        word = [0, 0, 0, 0]
        word[0] = (old_div(val, 1024)) * 4
        word[1] = (((old_div(val, 16)) & 0x3f) * 4) + 1
        word[2] = ((val & 0xf) * 4) + 2
        word[3] = (self.address * 4) + 3

        outstring = '%c%c%c%c' % (word[0], word[1], word[2], word[3])
        #   open and close it every time - not closing locks it out on windows
        self.ser.open()
        result = self.ser.write(outstring)
        self.ser.close()
        if (result != 4): return None
        return volt

    def close(self):
        self.ser.close()

    def get(self):
        return self.volt


if __name__ == '__main__':
    vsource = pyvbox(port=7)
    while (1):
        print('Enter voltage: ', end=' ')
        instring = sys.stdin.readline()
        print(instring)
        volt = string.atof(instring)
        if volt == -1: sys.exit()
        vsource.set(volt)
    print('bye!')
