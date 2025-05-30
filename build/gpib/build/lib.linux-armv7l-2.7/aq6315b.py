from __future__ import print_function
from builtins import range
from builtins import object
#!/usr/bin/env python
from Gpib_prologix_nt_ver2 import *
import time
import ctypes
import string
import numpy
import serial


class dev(object):
    def __init__(self, name, serialport):
        """Connect """
        self.meter = Gpib(name, serialport)
        meter = self.meter
        self.meter.flush_device_buffer()
        #  Not sure why we need 'SRQ1',  commented out because it seems to hangup prologix in Ubuntu 14.04
        #self.meter.write('SRQ1')

    def set_start(self, wav):
        msg = 'STAWL %.3f' % wav
        self.meter.write(msg)

    def set_stop(self, wav):
        msg = 'STPWL %.3f' % wav
        self.meter.write(msg)

    def set_center(self, wav):
        msg = 'CTRWL %.3f' % wav
        self.meter.write(msg)

    def set_span(self, wav):
        msg = 'SPAN %.1f' % wav
        self.meter.write(msg)

    def set_outwl(self, wav):
        msg = 'OUTWL %.3f' % wav
        self.meter.write(msg)

    def set_outbw(self, wav):
        msg = 'OUTBW %.3f' % wav
        self.meter.write(msg)

    def get(self, msg):
        self.meter.write(msg)
        time.sleep(.1)
        ret = self.meter.read(50)
        print(repr(ret))
        ret = string.split(ret, '\n')
        return float(ret[0])

    def get_start(self):
        msg = 'STAWL?\r\n'
        return self.get(msg)

    def get_stop(self):
        msg = 'STPWL?'
        return self.get(msg)

    def get_center(self):
        msg = 'CTRWL?'
        return self.get(msg)

    def single_trigger(self):
        rsp = self.meter.rsp()
        #print rsp
        msg = 'SGL'
        self.meter.write(msg)
        rsp = self.meter.rsp()
        while (rsp != 65):
            time.sleep(1)
            rsp = self.meter.rsp()
            #print 'RSP: %d'%(rsp)
        #msg = '*OPC'
        #self.meter.write(msg);
    def get_traceA_new(self):
        msg = 'LDATA'
        self.meter.write(msg)
        time.sleep(2)
        dmsg = ''
        n = 0
        while True:
            time.sleep(1)
            in_str = self.meter.read(10000)
            dmsg = dmsg + in_str
            n = n + 1
            print('loading trace' + n * '.')
            if '\r' in in_str:
                break
            if n > 30:
                print('error reading OSA')
                return None
                break

        #print dmsg
        data = numpy.fromstring(dmsg, sep=',')
        return data
        '''
    data = numpy.array([]);
    #print len(dlist)
    for item in dlist:
      #print item
      data = numpy.append(data,float(item));
    if (len(data)!= m_len):
      print 'Problem trying to down load data'
      print data
    #print data
    return data
    '''

    def get_traceA(self):
        msg = 'LDATA'
        self.meter.write(msg)
        c = self.meter.read(1)
        l = ''
        while (c != ','):
            l = l + c
            c = self.meter.read(1)
            #print c
        #c = string.split(c,',');
        #c = c[0];
        #print l
        m_len = int(l)
        #print m_len 
        dmsg = self.meter.read(20000)

        #print dmsg[-10:]
        endmsg = string.find(dmsg, '\r')
        #print endmsg
        #print len(dmsg)
        #time.sleep(1)
        #dmsg2= self.meter.read(10)
        #print len(dmsg2)
        if (endmsg > 0):
            dlist = string.split(dmsg[:endmsg], ',')
        else:
            dlist = string.split(dmsg, ',')

        data = numpy.array([])
        #print len(dlist)
        for item in dlist:
            #print item
            data = numpy.append(data, float(item))
        if (len(data) != m_len):
            print('Problem trying to down load data')
            print(data)
        #print data
        return data

    def get_Xaxis(self):
        msg = 'WDATA'
        self.meter.write(msg)
        time.sleep(1)
        c = self.meter.read(1)
        l = ''
        while (c != ','):
            l = l + c
            c = self.meter.read(1)
        m_len = int(l)
        #print m_len 
        dmsg = self.meter.read(20000)
        #print len(dmsg)
        #print dmsg
        endmsg = string.find(dmsg, '\r')
        #print endmsg
        if (endmsg > 0):
            dlist = string.split(dmsg[:endmsg], ',')
        else:
            dlist = string.split(dmsg, ',')
        data = numpy.array([])
        #print len(dlist)
        for item in dlist:
            data = numpy.append(data, float(item))
            #print len(data),
        #print len(data),
        if (len(data) != m_len):
            print('Problem trying to down load data')
            print(data)
        return data
        #start = self.get_start()
        #stop = self.get_stop()
        #span = self.get_span()
        #numpoints = self.get_numpoints();
        #step = (stop-start) / (numpoints-1.0);
        #wavelength = numpy.arange(start,stop+step,step)
        #return wavelength
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
    s = serial.Serial('/dev/ttyUSB2', 115200, timeout=0.5)
    dev1 = dev(13, s)
    dev1.meter.write('STAWL?\r\n')
    #time.sleep(5)
    dev1.meter.write('++read eoi\n')
    while True:
        msgin = dev1.meter.read()
        if len(msgin) > 0:
            break
    print('response 1:' + repr(msgin))
    #d=dev1.get_traceA_new()
    #print d
''' 
  loopcount = 0
  while True:
    print 'loop: %d %f'%(loopcount, dev1.get_start())
    loopcount = loopcount + 1 
  path = 'test.dat'
  import wx
  wxapp = wx.App(0)
  frame = wx.Frame(None, wx.ID_ANY,'frame');
  dlg = wx.FileDialog(
        frame, message="Save file as ...", defaultDir=os.getcwd(), 
        defaultFile="", style=wx.SAVE
        )
  if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
	directory = dlg.GetDirectory()
	name = dlg.GetFilename()
        print 'You selected "%s"' % path
	print name
	print path
        dev1 = dev('dev13')

        #f = open('test.dat','wb');
        #dev1.single_trigger()
        dev1.save_traceA(path)  
        dev1.close() 
	#a = input_raw('hello');
  dlg.Destroy()
'''
