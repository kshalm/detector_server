from __future__ import print_function
from builtins import str
from builtins import object
#!/usr/bin/env python
import Gpib
import time
from copy import deepcopy

params = [
    {
        'name': 'address',
        'type': 'int',
        'value': 4,
        'limits': (1, 32)
    },
    {
        'name': 'Coupling',
        'type': 'list',
        'values': {
            'DC': 'DC',
            'AC': 'AC'
        },
        'value': 'DC'
    },
    {
        'name': 'Impedance',
        'type': 'list',
        'values': {
            '50 Ohm': 50,
            '1 MOhm': 1e6
        },
        'value': 50
    },
    {
        'name': 'Threshold (V)',
        'type': 'float',
        'value': 0.1,
        'limits': (-1, 1)
    },
    {
        'name': 'Slope',
        'type': 'list',
        'values': {
            'Positive': 1,
            'Negative': -1
        },
        'value': 1
    },
    {
        'name': 'Totalize time',
        'type': 'float',
        'value': 1,
        'limits': (0, 1000)
    },
]


class dev(object):
    def __init__(self, addr, serialport=''):
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        meter = self.meter
        """Connect to and reset a HP35131A"""
        params[0]['value'] = self.addr
        #self.reset()
        #meter.write('ZERO:AUTO OFF')

    def identify(self):
        msg = '*IDN?'
        self.meter.write(msg)
        result = self.meter.read()
        return result

    def set_totalize(self):
        """set the counter to totalize, run when signaled,
    then total counts for 1 s.  change total time in program"""
        self.meter.write(':SENS:FUNC "TOT"')
        time.sleep(0.1)
        self.meter.write(':SENS:EVEN:LEV:AUTO OFF')
        time.sleep(0.1)
        self.meter.write(':SENS:TOT:ARM:SOUR IMM')
        time.sleep(0.1)
        self.meter.write(':SENS:TOT:ARM:STOP:SOUR TIM')
        time.sleep(0.1)
        self.meter.write('SENS:TOT:ARM:STOP:TIM 1')
        time.sleep(0.1)

    def get_function(self):
        msg = ':SENS:FUNC?'
        self.meter.write(msg)
        func = self.meter.read()
        return func.strip()

    def set_time(self, dt):
        msg = ':TOT:ARM:STOP:TIM %.3f' % dt
        self.meter.write(msg)
        time.sleep(0.1)

    def get_time(self):
        msg = ':TOT:ARM:STOP:TIM?'
        self.meter.write(msg)
        count_time = self.meter.read()
        #print count_time
        return count_time.strip()

    def set_threshold(self, v):
        msg = ':SENS:EVEN:LEV %fV' % v
        self.meter.write(msg)

    def get_threshold(self):
        msg = ':SENS:EVEN:LEV?'
        self.meter.write(msg)
        thresh = self.meter.read()
        return thresh.strip()

    def set_slope(self, slope):
        if slope >= 0:
            msg = ':SENS:EVEN:SLOP POS'
        else:
            msg = ':SENS:EVEN:SLOP NEG'
        self.meter.write(msg)

    def get_slope(self):
        msg = ':SENS:EVEN:SLOP?'
        self.meter.write(msg)
        thresh = self.meter.read()
        return thresh.strip()

    def set_input_coupling(self, coup):
        msg = ':INP1:COUP %s' % coup
        self.meter.write(msg)

    def get_input_coupling(self):
        msg = ':INP1:COUP?'
        self.meter.write(msg)
        coup = self.meter.read()
        return coup.strip()

    def set_impedance(self, r):
        msg = ':INP1:IMP %f OHM' % r
        self.meter.write(msg)
#  def set_impedance(self,r):
#      self.set_impedance(r)      

    def get_impedance(self):
        msg = ':INP1:IMP?'
        self.meter.write(msg)
        imp = self.meter.read()
        return imp.strip()

#  def get_impedance(self):
#      return self.get_impedance()

    def measure(self):
        msg = ':INIT'
        self.meter.write(msg)

    def set_continuous(self):
        msg = ':INIT:CONT ON'
        self.meter.write(msg)

    def get_tot_count(self):
        """Take a reading"""
        #self.meter.write('READ?')
        #reading = self.meter.read().split()

        #print 'Reading: '+reading[0]
        #return float(reading[0])
        gate = float(self.get_time())
        reading = self.meter.query('READ?', gate)
        # print '%.2f %s'%(gate,reading)
        try:
            return float(reading)
        except:
            return -1

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
                item['value'] = self.get_time()
            if 'value' in item:
                print(item['value'])

    def set_sens(self, sens, chan=1):
        sval = 0
        valid = False
        ts = str(type(sens))
        HighVal = 0
        MedVal = 50
        LowVal = 100
        if 'str' in ts:
            if sens[0] == 'H' or sens == 'h':
                valid = True
                sval = HighVal
            elif sens[0] == 'M' or sens == 'm':
                valid = True
                sval = MedVal
            elif sens[0] == 'L' or sens == 'l':
                valid = True
                sval = LowVal
        if 'int' in ts:
            if sens == 0:
                valid = True
                sval = HighVal
            if sens == 1 or (100 > sens > 2):
                valid = True
                sval = MedVal
            if sens == 2 or sens == 100:
                valid = True
                sval = LowVal
        if valid:
            self.meter.write(':SENS:EVEN%d:HYST:REL %d' % (chan, sval))
            #self.meter.write(':SENS:EVEN%d:HYST:REL?' %chan)
            #print 'Relitive hysteresis % is now: ' + self.meter.read()
        else:
            raise ValueError(
                'Invalid Input to setSens must be High, Med, Low, 0,1,2 or 0,50,100'
            )

    def get_sens(self, chan=1):
        self.meter.write(':SENS:EVEN%d:HYST:REL?' % chan)
        resp = self.meter.read()
        if '+0' in resp:
            return 'HIGH'
        if '+50' in resp:
            return 'MEDIUM'
        if '+100' in resp:
            return 'LOW'
        else:
            return -1

    def writeconfig(self, f):
        msg = self.identify().strip()
        f.write('# Counter is %s\n' % (msg))
        f.write('# Counter coupling is %s\n' % (self.get_input_coupling()))
        f.write('# Counter impedance is %s\n' % (self.get_impedance()))
        f.write('# Counter threshold is %s\n' % (self.get_threshold()))
        f.write('# Counter slope is %s\n' % (self.get_slope()))
        f.write('# Counter Function is %s\n' % (self.get_function()))
        f.write('# Counter totalize time is %s\n' % (self.get_time()))
        f.write('# Counter senstivity is %s \n' % (self.get_sens))
        f.flush()

    def reset(self):
        """Reset the DMM and it's registers."""
        self.meter.write('*RST')
        self.meter.write('*CLS')

    def close(self):
        """End communication with the DMM"""
        self.meter.close()

if (__name__ == '__main__'):
    #dev1 = dev('dev4')
    #dev1.set_totalize()
    #dev1.setTime(1)
    #while 1:
    #  a = dev1.read()/1.0
    #  print '%.2f'%a
    dev1 = dev(6, 'COM7')
    print(dev1.identify())
    dev1.close()
