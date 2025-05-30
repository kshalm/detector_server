from __future__ import print_function
from builtins import object
#!/usr/bin/env python
from Gpib import *
import time, string
debug = 0


class dev(object):
    def __init__(self, name):
        """Connect to and reset a Ortec974"""
        self.meter = Gpib(name)
        meter = self.meter
        #self.reset()
        #meter.write('ZERO:AUTO OFF')
    def start(self):
        self.meter.write('START\r')
        ack = self.meter.read()
        newline = string.find(ack, '\n')
        ack = ack[0:newline]
        if debug:
            print('start ack:', ack)

    def stop(self):
        loop = 1
        self.meter.write('STOP\r')
        ack = self.meter.read()
        newline = string.find(ack, '\n')
        ack = ack[0:newline]
        while loop:
            if debug:
                print('stop ack:', ack)
            loop = 0
            newline = string.find(ack, '\n')
            #data = int(ack[1:len(ack)])
            data = int(ack[1:newline])
            # fix crazy power up 
            if data == 1000070:
                loop = 1
                ack = self.meter.read()
                newline = string.find(ack, '\n')
                ack = ack[0:newline]

    def show(self):
        self.meter.write('SH_COU\r')
        data = self.meter.read()
        # fix crazy offset in reading problem if it occurs
        if data == '%000000069\n':
            ack = self.meter.read()
            ack = self.meter.read()
            self.meter.write('SH_COU\r')
            data = self.meter.read()
        ack = self.meter.read()
        newline = string.find(ack, '\n')
        ack = ack[0:newline]
        if debug:
            print('show ack:', ack)
        return data

    def set_counter_preset(self, m, n):
        self.stop()
        self.meter.write('SET_COU_PR %d,%d\r' % (m, n))
        ack = self.meter.read()
        #print 'set counter preset:'+ack
    def cl(self):
        self.meter.write('CL_COU\r')
        ack = self.meter.read()
        newline = string.find(ack, '\n')
        ack = ack[0:newline]
        if debug:
            print('cl ack:', ack)

    def read(self, t=1):
        self.stop()
        self.cl()
        self.start()
        time.sleep(t + .1)
        datastr = self.show()
        newline = string.find(datastr, '\n')
        datastr = datastr[0:newline]
        #datastr = string.replace(datastr,'\n','')
        #datastr = string.replace(datastr,'\r','')
        datastr = string.replace(datastr, ';', ' ')
        self.stop()
        if (debug):
            print('read: ' + datastr)
        return datastr

    def reset(self):
        """Reset the DMM and it's registers."""
        self.meter.write('*RST')
        self.meter.write('*CLS')

    def close(self):
        """End communication with the DMM"""
        self.meter.close()


if (__name__ == '__main__'):
    dev1 = dev('dev3')
    print(dev1.read(1))
    dev1.close()
