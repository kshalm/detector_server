from __future__ import print_function
from builtins import str
from builtins import range
from builtins import object
#!/usr/bin/env python
import sys, os, string, time
import Gpib
#import serial
import threading
from copy import deepcopy
import numpy as np
params = [
    {
        'name': 'AG81533A power meter GPIB Address',
        'type': 'int',
        'limits': (1, 32),
        'value': 5
    },
    {
        'name': 'AG81533A slot',
        'type': 'int',
        'limits': (1, 20),
        'value': 1
    },
]


def flt(s):
    try:
        #float(s)
        return float(s)
    except ValueError:
        return float('NaN')


#flt = ag8166.Gpib.flt


class dev(object):
    def __init__(self, addr, slot=3):
        self.meter = Gpib.Gpib(addr)
        self.gpibaddress = int(addr.lstrip('dev'))
        self.slot = slot
        self.set_atim(1)

    def get_param(self, msgout):
        self.meter.write(msgout)
        #while not(self.meter.rsp()&16):
        #    time.sleep(0.1)
        time.sleep(0.2)
        reply = self.meter.read().strip()
        #reply = self.meter.query(msgout,0.1)
        print('get_param: %s' % repr(reply.strip()))
        try:
            ret = float(reply.strip())
            return ret
        except:
            return float('NaN')

    def set_param(self, msgout, msgcheck, value):
        self.meter.write(msgout)
        ret = self.get_param(msgcheck)
        if ret != value:
            print('problem with %s' % msgout)
            raise Exception('problem with %s' % msgout)
            ret = float('NaN')
        return ret

    def get_cont(self):
        msgout = 'INIT%d:CONT?\n' % (self.slot)

        return int(self.meter.query(msgout))

    def set_cont(self, value):
        msg1 = 'INIT%d:CONT %d' % (self.slot, value)
        msg2 = 'INIT%d:CONT?' % (self.slot)
        self.cont = self.set_param(msg1, msg2, value)
        return self.cont

    def get_power(self):
        reply = self.meter.query('READ%d:POW?\n' % self.slot,
                                 0.5 + self.atim).strip()
        #print 'pow: ',repr(reply)
        """
      self.meter.write('READ%d:POW?\n'%self.slot)
      time.sleep(self.atim/2)
      while True:
          reply = self.meter.read().strip()
          if len(reply)>0:
              break;
          print 'Trying to read power again'
      """
        if len(reply) == 0:
            self.power = -1
            print(self.meter.read().strip())
        else:
            self.power = float(reply.strip())
        return self.power

    def get_lambda(self):
        msgout = 'SENS%d:POW:WAV?\n' % (self.slot)
        self.wl = self.get_param(msgout)
        return self.wl

    def set_lambda(self, value):
        self.meter.write('SENS%d:POW:WAV %fE-9\n' % (self.slot, value))
        self.wl = self.get_lambda() * 1e9
        if self.wl != value:
            print('problem setting wavelength to %f, %f' % (value, self.wl))
            self.meter.write('SENS%d:POW:WAV %fE-9\n' % (self.slot, value))
            self.wl = self.get_lambda() * 1e9

        return self.wl

    def get_atim(self):
        msg = 'SENS%d:POW:ATIM?\n' % self.slot
        self.atim = self.get_param(msg)
        #print repr(reply)
        return self.atim

    def set_atim(self, value):
        self.meter.write('SENS%d:POW:ATIM %f\n' % (self.slot, float(value)))
        self.atim = self.get_atim()
        if self.atim != value:
            print('problem setting atim to %f, %f' % (value, self.atim))
        return self.atim

    def get_range(self):
        msg = 'SENS%d:POW:RANG?\n' % (self.slot)
        self.range = int(self.get_param(msg))
        #print 'get_range:',reply
        return self.range

    def set_pow_autorange(self, auto):
        """turn auto range off or on"""
        msg = ':SENS%d:POW:RANG:AUTO %d' % (self.slot, auto)
        self.meter.write(msg)
        time.sleep(0.1)

    def set_range(self, value):
        self.set_pow_autorange(0)
        self.meter.write('SENS%d:POW:RANG %f\n' % (self.slot, value))
        self.range = self.get_range()
        if self.range != value:
            print('problem setting range to %f' % value)
        return self.range

    def set_unit(self, value):
        self.meter.write('SENS%d:POW:UNIT %f\n' % (self.slot, value))
        self.unit = self.get_unit()
        if self.unit != value:
            print('problem setting unit to %f' % value)
        return self.unit

    def get_unit(self):
        self.meter.write('SENS%d:POW:UNIT?\n' % self.slot)
        reply = self.meter.read(100).strip()
        self.unit = int(float(reply.strip()))
        return self.unit

    def identify(self):
        msg = '*IDN?'
        self.meter.write(msg)
        time.sleep(0.1)
        chassisid = self.meter.read().strip()
        """identify the module in a chosen slot"""
        slot = self.slot
        msg = ':SLOT%s:IDN?' % (str(slot))
        self.meter.write(msg)
        time.sleep(0.1)
        slotid = self.meter.read().strip()
        """identify the module in a chosen slot"""
        msg = ':SLOT%s:HEAD1:IDN?' % (str(slot))
        self.meter.write(msg)
        time.sleep(0.1)
        headid = self.meter.read().strip()

        return '# Chassis gpib %d: \t%s\n# Slot %d: \t\t%s\n# Head: \t\t%s\n' % (
            self.gpibaddress, chassisid, self.slot, slotid, headid)

    def writeconfig(self, f):
        msg = self.identify()
        #f.write('# Agilent 86142a in slot %d\n'%(self.slot))
        #f.write('#    ID: %s\n'%msg)
        f.write(msg)
        wl = self.get_lambda()
        atim = self.get_atim()
        rang = self.get_range()
        f.write('# wavelength: %e\n# ATIM: %f\n# Range: %d\n' %
                (wl, atim, rang))
        f.flush()

    def close(self):
        self.meter.close()

    def init_pwm_log(self, nreadings):
        self.nreadings = nreadings
        self.init_nreadings = nreadings

    def stop_pwm_log(self):
        self.nreadings = 0
        return

    def start_pwm_log(self):
        #self.measure_thread = threading.Thread(None, self.measure,args=(readings))
        self.readings = []
        self.nreadings = self.init_nreadings
        self.measure_thread = threading.Timer(0, self.measure, [self.readings])
        self.measure_thread.start()

    def measure(self, readings):
        #print self.nreadings
        if self.nreadings > 0:
            threading.Timer(1.01, self.measure, [readings]).start()
            readings.append(self.get_power())
            self.nreadings -= 1

    def measure2(self):
        readings = []
        for loop in range(self.nreadings):
            readings.append(self.get_power())
        self.nreadings = 0

    def read_pwm_log(self):
        while len(self.readings) < self.init_nreadings:
            time.sleep(1)
        return np.array(self.readings)

    def init_pwm_log_hp(self, num_points):
        #global s,addr,int_time,num_points,slot
        slot = self.slot
        self.log_num_points = num_points
        self.atim = self.get_atim()
        print('init power meter logging ATIM: %e' % self.atim)
        self.meter.write('SENS%d:FUNC:STAT LOGG, STOP\n' % slot)
        self.meter.write('SENS%d:FUNC:STAT?\n' % slot)
        reply = self.meter.read(100)
        #print reply.strip()
        int_time = self.atim
        self.meter.write('SENS%d:FUNC:PAR:LOGG %d, %.2f\n' %
                         (slot, num_points, int_time))
        self.meter.write('SENS%d:FUNC:PAR:LOGG?\n' % slot)
        #s.write('SENS%d:FUNC:PAR:STAB %d, %.1f, %.1f\n'%(slot,num_points,int_time,int_time))
        #s.write('SENS%d:FUNC:PAR:STAB?\n'%slot)

        reply = self.meter.read(100)
        print(reply.strip())

    def start_pwm_log_hp(self):
        self.meter.write('SENS%d:FUNC:STAT LOGG, STAR\n' % self.slot)
        #s.write('SENS%d:FUNC:STAT STAB, STAR\n'%slot)
    def stop_pwm_log_hp(self):
        self.meter.write('SENS%d:FUNC:STAT LOGG, STOP\n' % self.slot)

    def read_pwm_log_hp(self):
        #global s,addr,int_time, num_points,slot
        slot = self.slot
        #time.sleep(int_time*num_points)
        #time.sleep(num_points)
        while True:
            time.sleep(1)
            sys.stdout.write('.')
            sys.stdout.flush()
            reply = self.meter.query('SENS%d:FUNC:STAT?\n' % slot)
            #self.meter.write('SENS%d:FUNC:STAT?\n'%slot)
            #reply = self.meter.read(100)
            #print reply.strip()
            if 'COMPLETE' in reply:
                #print
                break
        self.meter.write('SENS%d:FUNC:RES?\n' % slot)

        msgin = self.meter.readbinary(2)
        print(repr(msgin))
        """
      msgin = self.meter.read(1)
      print repr(msgin)
      if len(msgin)==0:
          msgin = self.meter.read(1)
      print repr(msgin)
      """
        msgin = self.meter.readbinary(int(msgin[-1]))
        #print repr(msgin)
        total_len = int(msgin)
        #print total_len
        data_pwm = ''
        lefttoget = total_len
        while True:
            dat_out = self.meter.readbinary(lefttoget)
            lefttoget = lefttoget - len(dat_out)
            data_pwm = data_pwm + dat_out
            #print repr(dat_out)
            #print len(dat_out)
            #print 'lefttoget: ',lefttoget
            if lefttoget == 0:
                break
        """
      data_pwm=''
      lefttoget=self.log_num_points*4+5
      while True:
        dat_out = self.meter.read(lefttoget)
        if len(dat_out)==0:
          break
        lefttoget=lefttoget-len(dat_out)
        data_pwm=data_pwm+dat_out
        print 'lefttoget: ',lefttoget      
      """
        #print len(data_pwm)
        msgin = self.meter.read()
        #print 'end of pwmlog %s'%(repr(msgin))
        if msgin[0] != '\n':
            print('Problem with binary x-fer... Did not get \\n at the end')
        block = np.fromstring(data_pwm, dtype='float32')
        #print repr(data_pwm)
        #f = open('raw.out','wb')
        #f.write(data_pwm)
        #f.close()
        #print  block.shape   
        #return data_pwm
        return block

    def get_status(self):
        while True:
            self.meter.write('SENS%d:CORR:COLL:ZERO?' % self.slot)
            msgin = self.meter.read(100)
            #print 'msgin: '+repr(msgin)
            if len(msgin.strip()) > 0:
                break
            time.sleep(1)
        #print repr(msgin)
        self.status = int(msgin.strip())
        return self.status

    def zero(self):
        start = time.time()
        status = self.get_status()
        print('status before zero %d' % status)
        self.meter.write('SENS%d:CORR:COLL:ZERO' % (self.slot))
        # check status until zero is complete
        while True:
            status = self.get_status()
            #print 'zero status: %d'%status
            if status == 0:
                break
        print('zero time: %.2f' % (time.time() - start))

    def loc(self):
        self.meter.loc()


if __name__ == '__main__':
    meter = dev('dev11', 3)
    #meter = dev(8,'COM4',2)
    #print meter.meter.port
    #meter.set_cont(0)
    #print meter.get_cont()
    #print meter.set_atim(1)
    print(meter.get_power())
    print(meter.set_lambda(1537))
    #print meter.set_lambda(1566)
    meter.init_pwm_log(4)
    meter.start_pwm_log()
    msg = meter.read_pwm_log()
    print(msg)
    """
  meter.meter.tmo(12)
  meter.meter.config(12,0)
  meter.set_range(0)
  print 'range:',meter.get_range()
  print meter.identify()
  meter.set_cont(0)
  print meter.get_lambda()
  meter.zero()
  print meter.get_power()
  #meter.meter.eos()
  #print meter.get_lambda()
  print 'status:',meter.get_status()
  #meter.zero()
  #print meter.set_range(-10)
  print 'unit:',meter.set_unit(1)
  print 'pow:',meter.get_power()
  meter.set_pow_autorange(0)
  print 'range:',meter.get_range()
  meter.init_pwm_log(5)
  meter.start_pwm_log()
  msg = meter.read_pwm_log()
  print msg
  meter.start_pwm_log()
  msg = meter.read_pwm_log()
  print msg
  meter.stop_pwm_log()
  meter.loc()
  meter.set_lambda(1540)
  print meter.get_lambda()
 
  print meter.get_power()
  print meter.identify()
  meter.init_pwm_log(5)
  meter.start_pwm_log()
  msg = meter.read_pwm_log()
  print meter.get_power()
  print msg.mean() 
  print meter.get_range()
  meter.stop_pwm_log()
  meter.set_range(-10)
  meter.set_lambda(1470)
  import sys
  f = sys.stdout
  meter.writeconfig(f)
  meter.meter.loc()
  """
