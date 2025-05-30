from __future__ import print_function
from builtins import object
#!/usr/bin/env python
import sys, os, string, time
import serial
import threading


class device(object):
    def __init__(self, name):
        self.device = serial.Serial(name, baudrate=9600, timeout=1)

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

    def counterreset(self):
        self.write('CR')

    def counterstart(self):
        self.write('CS')

    def getcounterA(self):
        self.write('QA')
        return int(self.read())

    def getcounterB(self):
        self.write('QB')
        return int(self.read())

    def setdisclvlA(self, v):
        self.write('DL 0,%.4f' % v)

    def setdisclvlB(self, v):
        self.write('DL 1,%.4f' % v)


if (__name__ == '__main__'):
    filename = sys.argv[1]
    file = open(filename, 'w')
    dev1 = device('COM4')
    dev1.counterreset()
    dev1.counterstart()
    time.sleep(0.1)
    while (1):
        #dev1.counterreset();
        #dev1.counterstart();
        #time.sleep(1.2)
        a = 0
        b = 0
        #while ((a<=0) | (b<=0)):
        a = dev1.getcounterA()
        b = dev1.getcounterB()
        print('%d\t%d' % (int(a), int(b)))
    '''
  dev1.write('SD 1')
  counter=1
  nperiods=2000
  str = "NP %d"%nperiods
  dev1.write(str)
  while(1):
    print "Takeing buffer %d" %(counter),
    dev1.write('CR');
    dev1.write('CS');
    while(1):
      time.sleep(1);
      dev1.write('NN');
      a = dev1.read();
      if (a==nperiods):
	break;
    dev1.write('ET')
    print "reading %d"%counter
    for c in range(nperiods):
      a = dev1.read(); 
      b = dev1.read();
      str ='%d\t%d' %(a,b)
      #print "%d\t"%(c)+str
      file.write(str+'\n');
    file.flush()
    print str
    counter = counter+1;
    '''
    dev1.close()
