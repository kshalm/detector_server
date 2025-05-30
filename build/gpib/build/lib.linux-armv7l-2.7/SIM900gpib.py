from __future__ import print_function
from builtins import chr
from builtins import object
#!/usr/bin/env python
import sys, os, string, time
#from Gpib import *
#import serial
import threading
import Gpib

#print 'Hello'


class dev(object):
    def __init__(self, addr, serialport=''):
        """Connect to SIM900"""
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        """
    if type(addr) == list:
        self.p = addr  # should I make a deepcopy here?  Not sure, will not for now
        for item in self.p:
            if item.has_key('value'):
                name = item['name']
                value = item['value']
                if 'ddress' in name:
                    gpibaddress = value 
                elif 'GPIB interface name' in name:
                    portname = value
                    serialport = portname
                elif 'GPIB interface type' in name:
                    gpibtype = value

        print 'config from list addr %d, intf name %s, type %d'%(gpibaddress, portname, gpibtype)
        addr = gpibaddress
        if gpibtype==2:  # this is prologix
            self.meter = Gpib.Gpib(addr, port=portname)
        elif gpibtype==1:  # this is NI
            self.meter = Gpib.Gpib('dev%d'%addr)
            serialport = 'gpib0'
        else: # pretend it is an NI board
            self.meter = Gpib.Gpib('dev%d'%addr)
            serialport = 'gpib0'

    elif isinstance(addr,str):
      self.meter = Gpib.Gpib(addr)
    else:
      self.meter = Gpib.Gpib(addr,serialport)
    self.port = serialport
    self.addr = addr
    """
        #print 'Timeout: '+str(self.meter.timeout)
        self.meter.write("*RST\r")
        self.meter.write('FLSH\r')
        #time.sleep(0.2)
        self.meter.write('SRST\r')
        #time.sleep(0.2)
        self.meter.write('CEOI ON\n')
        self.meter.write('CEOI?\n')
        msg = self.meter.read(3)

        self.meter.write("*IDN?\r")
        # print 'initializing SIM900'    
        while True:
            msg = self.meter.read(80)
            # print 'check identity of SIM900',msg.strip()
            if 'SIM900' in msg:
                break
            elif 'SIM' in msg:
                self.meter.write('xyz')
                self.meter.write('*IDN?')

            #print msg

    def conna(self):
        outstring = "CONN a, \"xyz\"\r"  #conna is a hard-wired connection to auxiliary port a.
        self.meter.write(outstring)

    def conn(self, slot):
        outstring = "CONN %d,\"xyz\"\r" % slot
        #print outstring
        self.meter.write(outstring)

    def write(self, msg):
        outstring = "%s\r" % (msg)
        #print outstring
        self.meter.write(outstring)
        time.sleep(0)

    # this function is buggy. use getval2 instead. -burm
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
        data = self.meter.read()
        #print 'leng of message:%d\n'%len(data),
        #sys.stdout.write(data)
        #sys.stdout.flush()
        self.msg = data
        return data

    def reader(self):
        """loop forever and copy serial->console"""
        while 1:
            self.read()
#      data = self.meter.readline()
#      #print '%d:'%len(data),
#      sys.stdout.write(data)
#      sys.stdout.flush()
#      self.msg = data

    def readdmm(self):
        self.write(3, 'VOLT? 1')
        msg = self.getval(3)
        return msg

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
    def set(self, v):
        self.write(1, 'VOLT %.3f' % v)
        time.sleep(0.001)

    def setv(self, v):
        self.set(v)

    def getTempA(self):
        self.write(7, 'TVAL? 1')
        time.sleep(0)
        msg = self.getval2(7)
        try:
            return float(msg)
        except:
            return 0

    def getTempB(self):
        self.write(7, 'TVAL? 2')
        time.sleep(0)
        msg = self.getval2(7)
        try:
            return float(msg)
        except:
            return 0

    def getTempC(self):
        self.write(7, 'TVAL? 3')
        time.sleep(0)
        msg = self.getval2(7)
        try:
            return float(msg)
        except:
            return 0

    def getvals(self, channel):
        msg = self.getmsg(channel)
        res = []
        while (len(res) < 4):
            a = float(msg[0:msg.find(',')])
            msg = msg[(msg.find(',') + 2):]
            res = res + [a]
        return res

    def getval2(self, channel):
        msg = self.getmsg(channel)
        return msg

    def getTemps(self):
        self.write(2, 'TVAL? 0')

        time.sleep(0)
        vals = self.getvals(2)
        return vals

    def getVolts(self):
        self.write(2, 'VOLT? 0')
        time.sleep(0)
        vals = self.getvals(2)
        return vals

    def getRval(self, chan):
        self.write(chan, 'RVAL?')
        time.sleep(0)
        msg = self.getval2(chan)

        #self.meter.write('FLSH\r')
        return float(msg)

#  def getres(self):
#    while True:
#      try:
#        self.sim900.write(self.channel, 'RVAL?')
#        time.sleep(0.05)
#        val = self.sim900.getval(self.channel)
#        #print val
#        val = float(val)
#        break
#      except:
#        print   'Problem with getting rval '
#        time.sleep(0.01)
#    return val

    def setMUXch(self, ch):
        self.write(5, 'CHAN %d' % ch)

    def set_volt(self, ch, volt):
        self.conn(ch)
        self.write('VOLT %.3f' % volt)
        self.write('xyz')

    def get_src_volt(self, ch):
        self.conn(ch)
        self.write('VOLT?')
        msgin = self.read()
        self.write('xyz')
        return float(msgin)

    def set_power_on(self, ch):
        self.conn(ch)
        self.write('OPON')
        self.write('xyz')

    def set_power_off(self, ch):
        self.conn(ch)
        self.write('OPOF')
        self.write('xyz')

    def get_dvm_volt(self, slot, ch):
        a = 0
        while a < 2:
            #print a
            try:
                self.conn(slot)
                self.write('VOLT? %d' % ch)
                msgin = self.read()
                self.write('xyz')
                return float(msgin)
                break
            except ValueError:
                a = a + 1

    def v_src_identify(self, slot):
        self.conn(slot)
        msg = '*IDN?'
        self.write(msg)
        time.sleep(0.1)
        ret = self.read()
        print(repr(ret))
        self.write('xyz')
        return ret

    def close(self):
        self.meter.close()

if __name__ == '__main__':

    sim = dev('dev13')
    #print msg
    #print 'A:',sim.getTempA()
    a = sim.conn(7)
    sim.write('VOLT? 2')
    a = sim.read()
    print(a)
    sim.write('xyz')
    print(sim.get_dvm_volt(7, 2))
