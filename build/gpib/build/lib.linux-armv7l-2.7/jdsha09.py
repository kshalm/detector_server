from __future__ import print_function
from builtins import str
from builtins import object
#!/usr/bin/env python
import Gpib
import time
"""
params = [
{'name':'JDS attenuator GPIB Address','type':'int','limits':(1,32),'value':4},
]

Shane 2015_08_11
CommSet (Command Set):  Some of the JDS attenuators we have don't use the SCPI command set
So I've added an option to choose the command set used.  For example, the JDS Fitel HA9 uses 
the HA9 or HA8 comm set (see the programming manual for the differences between these and SCPI)
Ive modified the code here to accommodate HA9 only.  So if you're using a JDS that doesn't use SCPI, 
set it to use HA9.

CommSet options are SCPI or HA9.  The default is SCPI.
"""

CS = ['SCPI', 'HA9']


def flt(s):
    try:
        #float(s)
        return float(s)
    except ValueError:
        return float('NaN')


class dev(object):
    def __init__(self, addr, serialport='', CommSet=CS[0]):
        """Connect to jds, set in SCPI mode"""
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        self.cs = CommSet
        if self.cs not in CS:
            print(
                "You didn't set the CommSet value correctly.  See module header.  Closing port.  Goodbye"
            )
            self.close()
        #meter = self.meter
        #self.meter = Gpib(name)
        #meter = self.meter
        #self.reset()
        #meter.write('ZERO:AUTO OFF')

    def set_att(self, att):
        """Set the attenuation"""
        if self.cs == 'SCPI':
            msg = 'INP:ATT %.2f' % (att)
        elif self.cs == 'HA9':
            msg = 'ATT %0.2f dB \r\n' % att
        self.meter.write(msg)
        self.check(self.get_att, att, msg)

    def check(self, getFun, setVal, msg):
        val = float(getFun())

    def set_att_new(self, att):
        msg = 'INP:ATT %.2f;*WAI;INP:ATT?' % (att)
        val = flt(self.query(msg))
        if val != att:
            print('set %.2f/get %.2f' % (att, val))
            val = flt(self.query(msg))

    def set_att_orig(self, att):
        msg = 'INP:ATT %.2f' % (att)
        self.meter.write(msg)
        val = self.get_att()
        if val != att:
            print('set %.2f/get %.2f' % (att, self.get_att()))
            msg = 'INP:ATT %.2f' % (att)
            self.meter.write(msg)
            print('set %.2f/get %.2f' % (att, self.get_att()))

    def check(self, fun, x, msg):
        val = fun()

        cnt = 0
        while ('%0.2f' % val != '%0.2f' % (float(setVal))) and cnt < 10:
            cnt += 1
            print('set %.2f/get %.2f' % (float(setVal), val))
            print('Num tries: ', cnt)
            self.meter.write(msg)
            time.sleep(1)
            val = getFun()

    def set_lambda(self, wav):
        """Set the wavelength in nm"""
        if self.cs == 'SCPI':
            msg = ':INP:WAV %snm' % (str(wav))
        elif self.cs == 'HA9':
            msg = 'WVL %d nm' % (int(wav))
        self.meter.write(msg)
        self.check(self.get_lambda, wav * 1e-9, msg)

    def query(self, msg):
        reading = self.meter.query(msg)
        #print repr(reading)
        if len(reading) > 0:
            idx = len(reading) - 1 - reading[::-1].find('\x00')
            if idx < len(reading):
                reading = reading[(idx + 1):].strip()
                return reading
        else:
            return ''

    def query_new(self, msg):
        reading = self.meter.query(msg, 0.1)
        print('att query', repr(reading))
        reading = reading.replace('\x00', '')
        return reading

    def read(self):
        reading = self.meter.read()
        #print repr(reading)
        if reading[0] == '\x00':
            reading = reading[1:]
        #print repr(reading)
        return reading

    def get_lambda(self):
        """Get the attenuation"""
        if self.cs == 'SCPI':
            msg = ':INP:WAV?'
        elif self.cs == 'HA9':
            msg = 'WVL?\r\n'
        self.meter.write(msg)
        reading = self.read()
        return flt(reading)

    def get_att(self):
        """Get the attenuation"""
        if self.cs == 'SCPI':
            msg = ':INP:ATT?'
        elif self.cs == 'HA9':
            msg = 'ATT?\r\n'
        reading = self.query(msg)
        return flt(reading)
        """
    try:
      self.meter.write('INP:ATT?')
      reading = self.read()
      return float(reading)
    except self.meter.error:
      return None
    """

    def reset(self):
        """Reset the DMM and it's registers."""
        if self.cs == 'SCPI':
            msg = '*RST;*CLS'
        elif self.cs == 'HA9':
            msg = 'RESET; CLR \r\n'
        self.meter.write(msg)

    def enable(self):
        if self.cs == 'SCPI':
            msg = 'OUTP ON'
        elif self.cs == 'HA9':
            msg = 'D 0\r\n'
        self.meter.write(msg)

    def disable(self):
        if self.cs == 'SCPI':
            msg = 'OUTP OFF'
        elif self.cs == 'HA9':
            msg = 'D 1\r\n'
        self.meter.write(msg)

    def close(self):
        """End communication with the DMM"""
        self.meter.close()

    def identify(self):
        if self.cs == 'SCPI':
            msg = '*IDN?'
        elif self.cs == 'HA9':
            msg = 'IDN?\r\n'
        self.meter.write(msg)
        #time.sleep(0.1)
        chassisid = self.meter.read().strip()
        return '# JDS HA09: %s\n# gpib %d: \n' % (chassisid, self.addr)

    def writeconfig(self, f):
        msg = self.identify()
        #f.write('# Agilent 86142a in slot %d\n'%(self.slot))
        #f.write('#    ID: %s\n'%msg)
        f.write(msg)
        wl = self.get_lambda()
        att = self.get_att()
        f.write('# wavelength: %e\n# ATT: %f\n#\n' % (wl, att))
        f.flush()


if (__name__ == '__main__'):
    #dev1 = dev('dev4')
    dev1 = dev(5, 'COM11')
    #dev1.disable()
    dev1.set_att(10)
    a = dev1.get_att()
    print(a)
    import sys
    dev1.writeconfig(sys.stdout)
    dev1.close()
