from __future__ import print_function
from builtins import str
from builtins import range
#!/usr/bin/env python
import sys, os, string, time
import threading
import ag8166
import numpy as np
import copy
import logging

logger = logging.getLogger(__name__)
params = [
    {
        'name': 'AG81567A attenuator GPIB Address',
        'type': 'int',
        'limits': (1, 32),
        'value': 9
    },
    {
        'name': 'AG81567A slot',
        'type': 'int',
        'limits': (1, 20),
        'value': 1
    },
]


class dev(ag8166.dev):
    def __init__(self, addr, serialport='', slot=2):
        ag8166.dev.__init__(self, addr, serialport)
        if type(addr) == list:
            self.p = addr  # should I make a deepcopy here?  Not sure, will not for now
            for item in self.p:
                if 'value' in item:
                    name = item['name']
                    value = item['value']
                    if 'ddress' in name:
                        gpibaddress = value
                    elif 'slot' in name:
                        slot = value
            #print 'config from list addr %d, slot %d'%(gpibaddress, slot)
        elif type(addr) == str:
            # The arguments are shifted by 1
            gpibaddress = int(addr.strip('dev'))
            if type(serialport) == int:
                slot = serialport
        else:
            gpibaddress = addr
        self.slot = slot
        self.gpibaddress = gpibaddress
        self._range = -10
        #print type(gpibaddress)
        params[0]['value'] = gpibaddress
        params[1]['value'] = self.slot
        if not hasattr(self, 'p'):
            self.p = copy.deepcopy(params)
        self.att = None

    def get_lambda(self):
        reply = self.meter.query('INP%d:WAV?' % self.slot)
        self.wl = float(reply.strip())
        return self.wl

    def set_lambda(self, value):
        self.meter.write('INP%d:WAV %fE-9' % (self.slot, value))
        self.wl = self.get_lambda() * 1e9
        if self.wl != value:
            print('problem setting attenuator wavelength to %f' % value)
        return self.wl

    def get_att(self):
        # self.meter.write('INP%d:ATT?'%self.slot)
        # reply = self.meter.read(100).strip()
        # self.att = float(reply.strip())
        #
        # self.att = self.get_param('INP%d:ATT?'%self.slot)
        #
        self.att = self.meter.query('INP%d:ATT?' % self.slot)
        try:
            self.att = float(self.att.strip())
        except:
            logger.debug('problem with get_att')
            self.att = float('nan')
        return self.att

    def set_att(self, value):
        if self.att == None:
            self.att = self.get_att()
        while True:
            val = '%.2f' % value
            self.meter.write('INP%d:ATT %s' % (self.slot, val))
            wait = np.abs(self.att - value) * 3.0 / 60.
            time.sleep(wait)
            self.att = self.get_att()
            check = '%.2f' % self.att
            if check != val:
                print('problem setting attenuator to %s, gpib: %d, slot:%d, %s'
                      % (val, self.gpibaddress, self.slot, check))
            else:
                break
        return self.att

    def get_power(self):  # copied from power meter
        msg = 'FETC%d:POW?' % self.slot
        # self.power = self.get_param(msg) 
        self.meter.write(msg)
        msgin = ''
        count = 0
        while True:
            rsp = self.meter.rsp()
            # print(rsp)
            m = self.meter.read()
            msgin += m
            if '\n' in msgin:
                break
            count += 1
            if count == 10:
                break
        # print(count)
        try:
            self.power = float(msgin.strip())
        except:
            self.power = float('nan')
            print(' could not fetch power %s' % repr(msgin))
        return self.power
        """
        reply = self.meter.query('READ%d:POW?\n'%self.slot).strip()
        time.sleep(0)
        if len(reply)==0: 
            self.power = -1
            print self.meter.read().strip()
        else:
            self.power = float(reply.strip())
        return self.power
        """

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
        #self.lock = threading.RLock()
        #self.measure_thread = threading.Timer(0, self.measure,[self.readings])
        self.measure_thread = threading.Timer(0, self.measure)
        self.measure_thread.start()

    #def measure(self, readings):
    def wait(self):
        return

    def measure(self):
        self.measure_wait_before()

    def measure_wait_before(self):
        #start = time.time()
        for counter in range(self.nreadings):
            w_thread = threading.Timer(0.67, self.wait)
            w_thread.start()
            w_thread.join()
            with self.meter.lock:
                power = self.get_power()
            #print self, time.time(), power
            self.readings.append(power)
        #stop = time.time()
        #print 'dt:',stop-start
    def measure_wait_after(self):
        for counter in range(self.nreadings):
            power = self.get_power()
            self.readings.append(power)
            if counter == self.nreadings - 1:
                break
            w_thread = threading.Timer(1, self.wait)
            w_thread.start()
            w_thread.join()

    def read_pwm_log(self):
        #while self.nreadings>0:
        #while len(self.readings) != self.init_nreadings:
        #    time.sleep(1)
        self.measure_thread.join()
        #print 'read_pwm_log',self.readings
        return np.array(self.readings)

    def get_param(self, msgout):
        loop = True
        reply = self.meter.query(msgout)
        try:
            ret = float(reply.strip())
        except:
            ret = float('NaN')
        return ret

    def get_param_read(self, msgout):
        loop = True
        self.meter.write(msgout)
        reply = ''
        count = 0
        while loop:
            msgin = self.meter.read()
            reply += msgin
            if '\n' in msgin:
                break
            count += 1
            if count == 4:
                break
        try:
            ret = float(reply.strip())
        except:
            ret = float('NaN')
        return ret

    def get_param_old(self, msgout):
        loop = True
        while loop:
            self.meter.write(msgout)
            rsp = self.meter.rsp()
            count = 0
            while not (rsp & 16):
                rsp = self.meter.rsp()
                print(rsp)
                count += 1
                if count == 4:
                    break
            if count != 4:
                break
        reply = self.meter.read().strip()
        #reply = self.meter.query(msgout,0.1)
        print('get_param from att: %s' % repr(reply.strip()))
        try:
            ret = float(reply.strip())
            return ret
        except:
            return float('NaN')

    def set_range(self, value):
        self._range = value

    def get_range(self):
        return self._range

    def get_unit(self):  # copied from power meter
        msg = 'OUTP%d:POW:UNIT?' % self.slot
        unit = self.get_param(msg)
        # print repr(reply)
        if np.isnan(unit):
            unit = -1
        else:
            unit = int(unit)
        return unit

    def set_unit(self, value):  # copied from power meter
        self.meter.write('OUTP%d:POW:UNIT %f' % (self.slot, int(value)))
        unit = self.get_unit()
        if unit != value:
            print('problem setting unit to %f, %f' % (value, unit))
        return unit

    def get_atim(self):  # copied from power meter
        msg = 'OUTP%d:ATIM?' % self.slot
        self.atim = self.get_param(msg)
        # print repr(reply)
        return self.atim

    def set_atim(self, value):  # copied from power meter
        self.meter.write('OUTP%d:ATIM %f' % (self.slot, float(value)))
        self.atim = self.get_atim()
        if self.atim != value:
            print('problem setting atim to %f, %f' % (value, self.atim))
        return self.atim

    def get_pow_control(self):  # copied from power meter
        msg = 'OUTP%d:POW:CONTR?' % self.slot
        self.pow_control = self.get_param(msg)
        #print repr(reply)
        return self.pow_control

    def set_pow_control(self, value):  # copied from power meter
        self.meter.write('OUTP%d:POW:CONTR %d' % (self.slot, int(value)))
        self.pow_control = self.get_atim()
        if self.pow_control != value:
            print('problem setting pow contr to %d, %d' % (value, self.atim))
        return self.pow_control

    def get_outp_power(self):
        msg = 'OUTP%d:POW?' % self.slot
        self.outp_pow = self.get_param(msg)
        #print repr(reply)
        return self.outp_pow

    def enable(self):
        msg = 'OUTP%s:STAT ON' % (self.slot)
        self.meter.write(msg)
        time.sleep(0.1)

    def disable(self):
        msg = 'OUTP%s:STAT OFF' % (self.slot)
        self.meter.write(msg)
        time.sleep(0.1)

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
        return '# Chassis gpib %d: \t%s\n# Slot %d: \t\t%s\n' % (
            self.gpibaddress, chassisid, self.slot, slotid)

    def writeconfig(self, f):
        msg = self.identify()
        #f.write('# Agilent 86142a in slot %d\n'%(self.slot))
        #f.write('#    ID: %s\n'%msg)
        f.write(msg)
        wl = self.get_lambda()
        att = self.get_att()
        f.write('# wavelength: %e\n# ATT: %f\n#\n' % (wl, att))
        powermode = self.get_pow_control()
        set_power = self.get_outp_power()
        f.write('# power mode: %d\n# set_power: %f\n' % (powermode, set_power))
        f.flush()

    def close(self):
        self.meter.close()


if __name__ == '__main__':
    inst = dev('dev10', 9)
    # inst = dev(15,'COM11',3)
    #inst.meter.tmo()
    #print inst.get_lambda()
    #inst.set_lambda(1540)
    # print inst.get_atim()
    print(inst.get_lambda())
    print(inst.get_power())
    # print inst.get_power() 
    # print inst.get_outp_power()
    import sys
    f = sys.stdout
    inst.writeconfig(f)
    inst.meter.loc()
