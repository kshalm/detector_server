from __future__ import print_function
from builtins import chr
from builtins import object
#!/usr/bin/env python
import sys, os, string, time
import threading
from Gpib import *
import string


class dev(object):
    def __init__(self, addr, serialport=''):
        """Connect to SIM900"""

        # -- Add general declaration 3/3/2015 --
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        # -- end --

        #print name

        #self.meter = enhancedserial.Serial(name,baudrate=9600)
        #self.meter = Gpib(name)
        meter = self.meter
        self.meter.write('SRST\r')

    def set_power_on(self, slot):
        self.meter.write('CONN %d,"xyz"' % slot)
        self.meter.write('OPON')
        self.meter.write('xyz')

    def set_power_off(self, slot):
        self.meter.write('CONN %d,"xyz"' % slot)
        self.meter.write('OPOF')
        self.meter.write('xyz')

    def set_volt(self, slot, voltage):
        self.meter.write('CONN %d,"xyz"' % slot)
        time.sleep(0.1)
        msg = 'VOLT %f' % voltage
        self.meter.write(msg)
        time.sleep(0.1)
        self.meter.write('xyz')

    def get_src_volt(self, slot):
        self.meter.write('FLOQ')
        self.meter.write('CONN %d,"xyz"' % slot)
        #time.sleep(0.1)
        msg = 'VOLT?'
        self.meter.write(msg)
        #time.sleep(0.1)
        ret = self.meter.read()
        #time.sleep(0.1)
        self.meter.write('xyz')
        return float(ret)

    def get_dvm_volt(self, slot, channel):
        self.meter.write('CONN %d,"xyz"' % slot)
        #time.sleep(0.1)
        msg = 'VOLT? %d' % channel
        self.meter.write(msg)
        #time.sleep(0.1)
        ret = self.meter.read()
        #time.sleep(0.1)
        self.meter.write('xyz')
        return float(ret)

    def v_src_identify(self, slot):
        self.meter.write('CONN %d,"xyz"' % slot)
        time.sleep(0.1)
        msg = '*IDN?'
        self.meter.write(msg)
        time.sleep(0.1)
        ret = self.meter.read()
        time.sleep(0.1)
        self.meter.write('xyz')
        return ret

    def clearbuf(self, channel):
        time.sleep(0.01)
        len = float(self.getninp(channel))
        while (len > 0):
            time.sleep(0.01)
            val = self.getgetn(channel, len)
            #self.meter.clear()
            time.sleep(0.01)
            len = float(self.getninp(channel))
        time.sleep(0.01)

    def write(self, channel, msg):
        print(msg)
        outstring = "SNDT %d, '%s'\r" % (channel, msg)
        print(outstring)
        self.meter.write(outstring)
        time.sleep(0.01)

    def getval(self, channel):
        len = 0
        while len == 0:
            len = self.getninp(channel)
            #print 'msg len:', len
        oldlen = 0
        while oldlen != len:
            oldlen = len
            len = self.getninp(channel)
        time.sleep(0.01)
        #print self.meter.rsp()
        res = self.getgetn(channel, len)
        #print self.meter.rsp()
        return float(res)

    def getninp(self, channel):
        busy = 1
        while (busy == 1):
            #print  self.meter.rsp()
            outstring = 'NINP? %d\r' % channel
            self.meter.write(outstring)
            #print  self.meter.rsp()
            time.sleep(0.01)
            msg = self.meter.read()
            #print msg
            if len(msg) >= 2:
                try:
                    idx = string.find(msg, '\n')
                    #print 'idx',idx
                    #print "msg without linefeed '%s'"%msg[0:idx]
                    l = int(msg[0:idx])
                    busy = 0
                except:
                    print(sys.exc_info()[0])
                    print('Exception, msg', msg, len(msg))
                    busy = 0
                    l = -1
        return l

    def getgetn(self, channel, length):
        busy = 1
        res = ''
        #print 'getting %d'%length
        outstring = 'GETN? %d, %d\r' % (channel, length + 7)
        self.meter.write(outstring)
        while (1):
            c = self.meter.read(1)
            if c == '#':
                break
            else:
                print('First char: %d:"%c"' % (ord(c), c))
                return
#raise Error
        c = self.meter.read(1)
        #print ord(c),c
        numtoget = int(c)
        msg = self.meter.read(numtoget)
        numtoget2 = int(msg[0:numtoget])
        #print '%s: %d'%(msg[0:numtoget],numtoget2)
        msg = self.meter.read(numtoget2 + 1)
        #print msg
        #res = float(msg[0:numtoget2])
        msgs = string.split(msg)
        msg = msgs.pop()
        res = float(msg)
        return res

    def getmsg(self, channel):
        busy = 1
        while (busy == 1):
            l = self.getninp(channel)
            #print 'NINP: ',l
            res = self.getgetn(channel, l)
            res = res.replace(chr(13), '')
            res = res.replace(chr(10), '')
            #for i in range(len(res)):
            #  print ord(res[i]),res[i]
            if (len(res) > 0):
                busy = 0
        return res

    def read(self):
        data = self.meter.read()
        #print '%d:'%len(data),
        sys.stdout.write(data)
        sys.stdout.flush()
        self.msg = data

    def getres(self, channel):
        while True:
            try:
                self.write(channel, 'RVAL?')
                time.sleep(0.01)
                val = self.getval(channel)
                #print val
                val = float(val)
                break
            except:
                print('Problem with getting rval ')
                time.sleep(0.01)
        return val

    def reader(self):
        """loop forever and copy serial->console"""
        while 1:
            self.read()

#      data = self.meter.readline()
#      #print '%d:'%len(data),
#      sys.stdout.write(data)
#      sys.stdout.flush()
#      self.msg = data

    def test(self):
        outstring = 'SSCR?\r'
        self.meter.write(outstring)
        #msg = self.meter.read()
        #print msg 
if __name__ == '__main__':

    port = 2
    if (len(sys.argv) > 1):
        port = string.atoi(sys.argv[1])
    #sim = device('COM1:')
    sim = device('dev2')
    sim.write(1, 'RVAL?')
    msg = sim.getval(1)
    #print msg
    sim.meter.close()
