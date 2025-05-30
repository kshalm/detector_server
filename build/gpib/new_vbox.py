from __future__ import print_function
from builtins import object
#!/usr/bin/env python
import sys, os, serial, string


class pyvbox(object):
    def __init__(self, port=1, baud=9600, address=0):
        port = '\\\\.\\COM%d' % port
        self.ser = serial.Serial(port=port, baudrate=115200)  #(0,baud)
        self.voltage = None
        self.ser.close()

    def set(self, volt):
        if (volt < 0 or volt > 6.5535): return None
        self.voltage = volt

        # 1 bit = 100 uV
        val = int(volt * 10000.0 + 0.5)
        #val = volt   

        #     word0  high6bit 00
        #     word1  mid6bit 01
        #     word2  low4bit 10
        #     word3  address 11   -  address is 4 bits

        word = [0, 0, 0]
        word[0] = (val & 0x7F) << 1
        #least sig 7 bits
        word[1] = ((val >> 7) & 0x7f) << 1
        word[2] = (((val >> 14) & 0x3) << 1) + 0x51

        outstring = '%c%c%c' % (word[0], word[1], word[2])
        #   open and close it every time - not closing locks it out on windows
        self.ser.open()
        result = self.ser.write(outstring)
        self.ser.close()
        if (result != 4): return None
        return volt

    def get(self):
        return self.volt

    def setPort(self, port):
        self.ser.setPort(port)
        print(self.ser)


if __name__ == '__main__':
    vsource = pyvbox(port=6)
    while (1):
        print('Enter voltage: ', end=' ')
        instring = sys.stdin.readline()
        print(instring)
        volt = string.atof(instring)
        if volt == -1: sys.exit()
        vsource.set(volt)
    print('bye!')
