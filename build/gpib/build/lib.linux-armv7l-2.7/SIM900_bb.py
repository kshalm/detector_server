from __future__ import print_function
from builtins import chr
from builtins import object
#!/usr/bin/env python
import sys, os, string, time
from Gpib import *
import threading

#print 'Hello'


class device(object):
    def __init__(self, addr, serialport=''):
        """Connect to SIM900"""
        # -- Add general declaration 3/3/2015 --
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        # -- end --

        # self.meter = Gpib(name)
        self.meter.write('FLSH\r')
        time.sleep(0.2)
        self.meter.write('SRST\r')
        time.sleep(0.2)

    def write(self, channel, msg):
        outstring = "SNDT %d, '%s'\r" % (channel, msg)
        #print outstring
        self.meter.write(outstring)
        time.sleep(0)

    # in case getval() has a bug, try getval2. -burm
    def getval(self, channel):
        loop = 1
        while (loop):
            outstring = 'NINP? %d\r' % channel
            #print outstring
            self.meter.write(outstring)
            msg = self.meter.read()
            #print len(msg),":",msg,':',msg.find(chr(10)),
            msg = msg[0:msg.find(chr(10))]
            #print len(msg),":",msg
            if int(msg) > 0:
                loop = 0
        loop = 1
        while (loop):
            outstring = 'NINP? %d\r' % channel
            #print outstring
            self.meter.write(outstring)
            msg = self.meter.read()
            #print len(msg),":",msg,':',msg.find(chr(10)),
            msg = msg[0:msg.find(chr(10))]
            #print len(msg),":",msg
            if int(msg) > 0:
                loop = 0  #outstring = 'GETN? %d, %d\r'%(channel,int(msg)+7)
        outstring = 'GETN? %d, %d\r' % (channel, 100)
        #print outstring
        self.meter.write(outstring)
        #time.sleep(1)
        res = self.meter.read(1)
        #print res
        res = self.meter.read(1)
        #print res
        res = self.meter.read(int(res))
        #print res
        res = self.meter.read(int(res) + 1)
        #print len(res),
        res = res.replace(chr(13), '')
        res = res.replace(chr(10), '')
        #print len(res),res
        #self.meter.ibrsp()
        try:
            ans = float(res)
        except:
            ans = -1
        return ans

    def getninp(self, channel):
        loop = 1
        oldvalue = -1
        while (loop):
            outstring = 'NINP? %d\r' % channel
            #print outstring
            self.meter.write(outstring)
            msg = self.meter.read()
            #print 'a:',len(msg),":",msg,':',msg.find(chr(10))
            msg = msg[0:msg.find(chr(10))]
            #print 'b:',len(msg),":",msg
            if oldvalue > 0:
                if (int(msg) == oldvalue):
                    loop = 0
            oldvalue = int(msg)
            #print msg
        loop = 1

        return int(msg)

    def oldgetninp(self, channel):
        busy = 1
        while (busy == 1):
            outstring = 'NINP? %d\r' % channel
            self.meter.write(outstring)
            #msg = self.meter.readline()
            msg = self.meter.read(100)
            print('msg: ', msg)
            if len(msg) > 2:
                try:
                    l = int(msg[0:(len(msg) - 2)])
                    busy = 0
                except:
                    print('msg', msg)
                    busy = 1
        return l

    def getgetn(self, channel, length):
        res = ''
        #print 'getting %d'%length
        outstring = 'GETN? %d, %d\r' % (channel, length + 7)
        self.meter.write(outstring)
        c = self.meter.read(1)
        #print ord(c),c
        c = self.meter.read(1)
        #print ord(c),c
        numtoget = int(c)
        msg = self.meter.read(numtoget)
        numtoget = int(msg)
        res = self.meter.read(numtoget + 1)
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
        data = self.meter.readline()
        #print '%d:'%len(data),
        sys.stdout.write(data)
        sys.stdout.flush()
        self.msg = data

    def reader(self):
        """loop forever and copy serial->console"""
        while 1:
            self.read()

#      data = self.meter.readline()
#      #print '%d:'%len(data),
#      sys.stdout.write(data)
#      sys.stdout.flush()
#      self.msg = data

    def readdmm(self, ch):
        self.write(3, 'VOLT? %d' % ch)
        msg = self.getval2(3)
        return float(msg)

    def test(self):
        #sim.set(0.1)
        #time.sleep(1)
        #self.write(3,'VOLT? 1')
        #msg = self.getval(3)    
        self.write(2, 'CINI? 1')
        msg = self.getmsg(2)
        print(msg)
        #outstring = 'SSCR?\r'
        #self.meter.write(outstring)
        #msg = self.meter.read()
        #print msg 
    def set(self, ch, v):
        self.write(ch, 'VOLT %.3f' % v)
        time.sleep(0.001)

    def setv(self, ch, v):
        self.set(ch, v)

    def readv(self, ch):
        self.write(ch, 'VOLT?')
        time.sleep(0.1)
        msg = self.getval2(ch)
        return float(msg)

    def von(self, ch):
        self.write(ch, 'OPON')

    def voff(self, ch):
        self.write(ch, 'OPOF')

    def getTempA(self):
        self.write(1, 'TVAL? 1')
        time.sleep(0)
        msg = self.getval(2)
        return float(msg)

    def getTempB(self):
        self.write(1, 'TVAL? 2')
        time.sleep(0)
        msg = self.getval(2)
        return float(msg)

    def getvals(self, channel):
        msg = self.getmsg(channel)
        res = []
        while (len(res) < 4):
            a = float(msg[0:msg.find(',')])
            msg = msg[(msg.find(',') + 2):]
            res = res + [a]
        return res

    def getval2(self, channel):
        time.sleep(0.1)
        self.meter.write('GETN? %d,100' % channel)
        time.sleep(0.1)
        msg = self.meter.read()
        msg = msg[5:]
        return msg

    def a2flist(self, msg):
        strvals = msg.split(',')
        #print msg
        #print strvals
        vals = []
        for strval in strvals:
            vals = vals + [float(strval)]
        return vals

    def getTemps922(self, channel):
        self.write(channel, 'TVAL? 0')
        time.sleep(0.2)
        msg = self.getval2(channel)
        return self.a2flist(msg)

    def getVolts922(self, channel):
        self.write(6, 'VOLT? 0')
        time.sleep(0.1)
        msg = self.getval2(channel)
        return self.a2flist(msg)

    def getRval921(self, channel):
        self.write(channel, 'RVAL?')
        time.sleep(0.2)
        msg = self.getval2(channel)
        return self.a2flist(msg)[0]

if __name__ == '__main__':

    sim = device('dev2')
    #print msg
    #print 'A:',sim.getTempA()
    a = sim.getVolts922(6)
    print(a)
    a = sim.getTemps922(6)
    print(a)
    a = sim.getRval921(4)
    print(a)
