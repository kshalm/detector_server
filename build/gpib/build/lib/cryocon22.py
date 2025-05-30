from __future__ import print_function
from builtins import chr
from builtins import range
from builtins import object
#!/usr/bin/env python
import sys, os, string, time
import enhancedserial
import threading


class device(object):
    def __init__(self, name):
        """Connect to SIM900"""
        #print name
        self.name = name
        self.open()
        #self.meter.write("\nSYSTEM:REMLED?\n") 
        #ans = self.meter.readline()
        #print ans
        #self.meter.readline()
        #self.meter.write("SYSTEM:LOOP ON\n")
    def open(self):
        self.meter = enhancedserial.Serial(
            self.name, baudrate=9600, timeout=1, writeTimeout=1)

    def close(self):
        self.meter.close()

    def write(self, msg):
        outstring = "%s\n" % (msg)
        #print "writing: ",outstring
        self.meter.write(outstring)
        time.sleep(0)

    def getValue(self, msg):
        loop = 1
        self.write(msg)
        while loop:
            #time.sleep(1)
            ret = self.getval()
            if (ret != None):
                loop = 0
            else:
                self.write(msg)
        return ret

    def getval(self):
        res = self.meter.readline()
        #print len(res),res
        res = res.replace(chr(13), '')
        res = res.replace(chr(10), '')
        #print 'replaced whitespace',len(res),res
        if (len(res) == 0):
            print('No result', len(res), res)
            return None
        else:
            return float(res)

    def getTempA(self):
        self.write("INPUT? A")
        return self.getval()

    def getTempB(self):
        return self.getValue('INPUT? B')

#    self.write("INPUT? B")
#    return self.getval()

    def setSetPt(self, loopnum, value):
        outstring = 'LOOP %d:SETPT %.1f' % (loopnum, value)
        #print outstring
        self.write(outstring)
        #print 'hello',
        #print self.getSetPt(loopnum)
    def getSetPt(self, loopnum):
        outstring = 'LOOP %d:SETPT?' % (loopnum)
        self.write(outstring)
        self.meter.flush()
        return self.getval()

    def setPgain(self, loopnum, value):
        outstring = 'LOOP %d:PGAIN %f' % (loopnum, value)
        self.write(outstring)

    def getPgain(self, loopnum):
        outstring = 'LOOP %d:PGAIN?' % (loopnum)
        self.write(outstring)
        return self.getval()

    def setIgain(self, loopnum, value):
        outstring = 'LOOP %d:IGAIN %f' % (loopnum, value)
        self.write(outstring)

    def getIgain(self, loopnum):
        outstring = 'LOOP %d:IGAIN?' % (loopnum)
        self.write(outstring)
        return self.getval()

    def getMaxA(self):
        return self.getValue('INP A:MAX?')

    def getMaxB(self):
        outstring = 'INP B:MAX?'
        self.write(outstring)
        return self.getval()

    def getMinA(self):
        outstring = 'INP A:MIN?'
        self.write(outstring)
        return self.getval()

    def getMinB(self):
        outstring = 'INP B:MIN?'
        self.write(outstring)
        return self.getval()

    def getVarA(self):
        outstring = 'INP A:VAR?'
        self.write(outstring)
        return self.getval()

    def getVarB(self):
        outstring = 'INP B:VAR?'
        self.write(outstring)
        return self.getval()

    def getTime(self):
        outstring = 'STATS:TIME?'
        self.write(outstring)
        return self.getval()

    def resetTime(self):
        outstring = 'STATS:RESET'
        self.write(outstring)

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

    def sweep_PI(self):
        Tset = 3
        Tstep = 0.2
        filename = 'scan_PI.data'
        file = open(filename, 'w')
        while (Tset < 5.1):
            #print self.getSetPt(1)
            self.setSetPt(1, Tset)
            for P in range(1, 21, 2):
                self.setPgain(1, P)
                for I in range(0, 11, 2):
                    self.setIgain(1, I)
                    start = time.time()
                    t = start
                    while ((t - start) < 300):
                        outstring = ''
                        t = time.time()
                        outstring = outstring + '%.2f\t%.2f\t%d\t%d' % (
                            t, Tset, P, I)
                        outstring = outstring + '\t%f' % (sim.getTempA())
                        outstring = outstring + '\t%f' % (sim.getTempB())
                        print(outstring)
                        file.write(outstring + '\n')
                        file.flush()
            Tset = Tset + Tstep
if __name__ == '__main__':
    port = 1
    if (len(sys.argv) > 1):
        port = string.atoi(sys.argv[1])
    #sim = device('/dev/ttyUSB1')
    sim = device('COM7')
    print(sim.getTempB())
    sim.sweep_PI()
    #loop = 1
    #while (loop): 
    #  try: 
    #    sim.setSetPt(1,3.0)
    #    loop = 0
    #  except:
    #    loop = 1
    #    print  sys.exc_info()[1]
    #    time.sleep(1)
    #    sim.close()
    #    sim.open()

    #cept:
    #  print "error"
    #print sim.getPgain(1)
    #try:
    #  sim.setPgain(1,3.0)
    #except:
    #  print "error"
    #print sim.getPgain(1)
    #sim.write('INPUT? A')
    #msg = sim.getval()
    #val = sim.getTempA()
    #print 'val',val
    #for i in range(100):
    #  print i,sim.getTempA(),sim.getTempB()
    #print sim.getTempB()
    #print 'P: ',sim.getPgain(1)
    #print 'I: ',sim.getIgain(1)
    #print 'Time: ',sim.getTime()
    #print 'MinA: ',sim.getMinA()
    #print 'MaxA: ',sim.getMaxA()
    #print 'MaxA: ',sim.getMaxA()
    #print 'VarA: ',sim.getVarA()
