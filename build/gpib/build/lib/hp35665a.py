from __future__ import print_function
from builtins import range
from builtins import object
#!/usr/bin/env python
import Gpib
import time
import numpy
import sys
from copy import deepcopy
params = [{'name': 'address', 'type': 'int', 'value': 12, 'limits': (1, 32)}, ]


class dev(object):
    def __init__(self, addr, serialport=''):
        if isinstance(addr, str):
            self.meter = Gpib.Gpib(addr)
        else:
            self.meter = Gpib.Gpib(addr, serialport)
        """Connect to and reset a HP35131A"""
        meter = self.meter
        self.addr = addr
        self.serialport = serialport
        params[0]['value'] = addr
        self.p = deepcopy(params)
        #self.reset()
        #meter.write('ZERO:AUTO OFF')
    def reinit(self):
        self.close()
        self.meter.port.close()
        if isinstance(self.addr, str):
            self.meter = Gpib.Gpib(self.addr)
        else:
            self.meter = Gpib.Gpib(self.addr, self.serialport)

    def identify(self):
        msg = '*IDN?'
        self.meter.write(msg)
        result = self.meter.read()
        return result

    def get_trace_unit(self, trace):
        msg = 'CALC%d:UNIT:VOLT?' % trace
        self.meter.write(msg)
        result = self.meter.read()
        return result

    def get_freq_asc(self, trace):
        msg = 'TRAC:X? TRAC%d' % trace
        self.meter.write(msg)
        time.sleep(0.1)
        print('getting data')
        msg = ''
        return self.read_array()

    def get_freq_bin(self, trace):
        msg = 'FORM:DATA REAL,64'
        self.meter.write(msg)
        msg = 'TRAC:X? TRAC%d' % trace
        self.meter.write(msg)
        time.sleep(0.1)
        print('getting data')
        return self.read_array_bin()

    def read_array_bin(self):
        loop = True
        msgin = self.meter.read(1)
        length = 0
        if msgin != '#':
            loop = False
        else:
            msgin = self.meter.read(1)
            length = self.meter.read(int(msgin))
            length = int(length)
            #print 'length: %d'%(length)
        msg = ''
        while loop:
            msgin = self.meter.read(length)
            msg = msg + msgin
            length = length - len(msgin)
            if length <= 0:
                break
        #print len(msg)
        array = numpy.fromstring(msg, dtype=numpy.dtype('>f8'))
        #print array,len(array)
        print('reinit the serial port')
        self.reinit()
        return array

    def read_array(self):
        msg = ''
        while True:
            msgin = self.meter.read(512)
            #print repr(msgin)
            time.sleep(.1)
            msg = msg + msgin
            if msgin[-1] == '\n':
                break
        msg = msg.strip()
        print('reinit the serial port')
        self.reinit()
        #print msg
        array = numpy.fromstring(msg, sep=',')
        #print array
        return array

    def get_trace_asc(self, trace=1):
        self.meter.write('CALC%d:DATA?' % trace)
        msg = ''
        time.sleep(0.1)
        return self.read_array()

    def get_trace_bin(self, trace=1):
        msg = 'FORM:DATA REAL,64'
        self.meter.write(msg)
        self.meter.write('CALC%d:DATA?' % trace)
        time.sleep(0.1)
        return self.read_array_bin()

    def get_params_from_inst(self):
        """ Read settings from the instrument and load them in the params varialbe """
        for item in self.p:
            if 'value' in item:
                print(item['name'], item['value'])
            if item['name'] == 'Coupling':
                item['value'] = self.get_input_coupling()
            elif item['name'] == 'Impedance':
                item['value'] = float(self.get_impedance())
            elif item['name'] == 'Threshold (V)':
                item['value'] = float(self.get_threshold())
            elif item['name'] == 'Slope':
                data = self.get_slope()
                if data == 'POS':
                    item['value'] = 1
                else:
                    item['value'] = -1
            elif item['name'] == 'Totalize time':
                item['value'] = float(self.get_time())
            if 'value' in item:
                print(item['value'])

    def writeconfig(self, f):
        msg = self.identify().strip()
        f.write('# Counter is %s\n' % (msg))
        f.write('# Counter coupling is %s\n' % (self.get_input_coupling()))
        f.write('# Counter impedance is %s\n' % (self.get_impedance()))
        f.write('# Counter threshold is %s\n' % (self.get_threshold()))
        f.write('# Counter slope is %s\n' % (self.get_slope()))
        f.write('# Counter totalize time is %s\n' % (self.get_time()))
        f.flush()

    def reset(self):
        """Reset the DMM and it's registers."""
        self.meter.write('*RST')
        self.meter.write('*CLS')

    def close(self):
        """End communication with the DMM"""
        self.meter.close()


if (__name__ == '__main__'):
    dev1 = dev(12, '/dev/ttyUSB1')
    """
  psd = dev1.get_trace(1)
  print psd,len(psd)
  """
    print(dev1.identify().strip())
    psd = dev1.get_trace_bin(1)

    print(dev1.identify().strip())
    freq = dev1.get_freq_bin(1)
    #dev1.close()
    #print len(freq)
    #print 'try gpib 1 '+dev1.identify().strip()
    #print 'try gpib again'
    dev1.close()
    f = open(sys.argv[1], 'w')
    for i in range(len(psd)):
        f.write('%d %e\n' % (freq[i], psd[i]))
        f.flush()
    f.close()
