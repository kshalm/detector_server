from __future__ import division
from __future__ import print_function
from builtins import chr
from builtins import range
from past.utils import old_div
import base_optical_power_meter
import Gpib
import threading
import time
import string
import numpy as np
DEBUG = False
params = [
    {
        'name': 'AQ8233 GPIB Address',
        'type': 'int',
        'limits': (1, 32),
        'value': 4
    },
    {
        'name': 'AQ8233 Slot',
        'type': 'int',
        'values': {1, 2, 3},
        'value': 3
    },
]

rng_list = np.arange(30, -70, -10)
rng_dict = {}
for i, val in enumerate(rng_list):
    rng_dict[int(val)] = chr(ord('C') + i)
rng_dict[111] = chr(
    65)  #  Shane changed this so I can set the OPM range to auto.
atime_dict = {}
atime_list = [1, 2, 5, 10, 20, 50, 100, 200]
unit_dict = {
    'L': 9,
    'M': 6,
    'N': 3,
    'O': 0,
    'P': -3,
    'Q': -6,
    'R': -9,
    'S': -12,
    'T': -15,
    'Z': -18
}

for i, val in enumerate(atime_list):
    atime_dict[int(val)] = chr(ord('A') + i)


def find_key(d, v):
    for key, value in list(d.items()):
        if v == value:
            return key
    return None


class dev(base_optical_power_meter.dev):
    def __init__(self, addr, serialport='', slot=1):
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        meter = self.meter
        #  fill in correct values for params, and make a copy of this instance
        if type(addr) == list:
            self.p = addr  # should I make a deepcopy here?  Not sure, will not for now
            for item in self.p:
                if 'value' in item:
                    name = item['name']
                    value = item['value']
                    if 'ddress' in name:
                        gpibaddress = value
                    elif 'Slot' in name:
                        slot = value
            print('config from list addr %d, slot %d, ch %d' %
                  (gpibaddress, slot, ch))
        elif type(addr) == str:  # Arguments are shifted by 1
            gpibaddress = int(addr.strip('dev'))
            if type(serialport) == int:
                slot = serialport

        else:
            gpibaddress = addr
        self.slot = slot
        self.addr = gpibaddress
        params[0]['value'] = gpibaddress
        params[1]['value'] = slot
        if not hasattr(
                self, 'p'
        ):  # create attribute p because class was instantiated w/o list
            self.p = deepcopy(params)
        self.std_init()

    def std_init(self):
        return

    def identify(self):
        #chassisid = super(dev, self).identify()
        #self.meter.write('C%d'%self.slot)
        # should we do a MOD?
        #slotid = self.meter.query('MODEL?',0.1).strip()
        #slotid = self.meter.query('MOD?',0.1)
        return '# Chassis gpib %d: \t%# Slot %d: \n' % (self.addr, self.slot)

    def writeconfig(self, fp):
        super(dev, self).writeconfig(fp)
        fp.flush()

    def get_range(self):
        self.meter.write('C%d' % self.slot)
        msg = self.meter.query('DS%d, S' % self.slot)
        value = msg.strip().lstrip('PR')
        key = None
        for k in list(rng_dict.keys()):
            if rng_dict[k] == value:
                key = k
                break
        if key == None:
            key = float('NaN')
        return key

    def set_range(self, value):
        self.meter.write('C%d' % self.slot)
        rng = rng_dict[int(value)]
        self.meter.write('PR%c' % rng)
        if value != self.get_range():
            print('Problem setting power meter range to %d, gpib: %d, slot: %d'
                  % (value, self.addr, self.slot))
        return rng

    def get_lambda(self):
        loop = 0
        while loop < 3:
            self.meter.write('C%d' % self.slot)
            msg = self.meter.query('PW?')
            if len(msg) == 0:
                msg = self.meter.read()
            msg = msg.strip()
            #print loop,repr(msg)
            if len(msg) > 0:
                self.wl = float(msg.strip().lstrip('PW'))
                return self.wl
            else:
                loop += 1
        print('Problem getting the wavelength from the power meter')
        self.wl = -1
        return self.wl
        """
        self.meter.write('C%d'%self.slot)
        msg = self.meter.query('PW?')
        self.wl = float(msg.strip().lstrip('PW'))
        return self.wl 
        """

    def set_lambda(self, value):
        self.meter.write('C%d' % self.slot)
        value = int(value)
        self.meter.write('PW%d' % int(value))
        time.sleep(0.5)
        wl = self.get_lambda()
        if value != wl:
            print(
                'Problem setting wavelength on the power meter to %d, gpib: %d, slot: %d got:%f'
                % (value, self.addr, self.slot, wl))
            return -1
        return 0

    def get_atim(self):
        self.meter.write('C%d' % self.slot)
        msg = self.meter.query('PA?')
        value = msg.strip().lstrip('PA')
        key = None
        for k in list(atime_dict.keys()):
            if atime_dict[k] == value:
                key = k
                break
        if key == None:
            key = float('NaN')
        return key

    def set_atim(self, value):
        self.meter.write('C%d' % self.slot)
        atime = atime_dict[value]
        self.meter.write('PA%c' % atime)
        if value != self.get_atim():
            print('Problem setting power meter atime to %d, gpib: %d, slot: %d'
                  % (value, self.addr, self.slot))
        return None

    def set_unit(self, value):
        self.meter.write('C%d' % self.slot)
        if value == 1:
            self.meter.write('PFA')  #  Watt
        elif value == 0:
            self.meter.write('PFB')  # dBm
        return None

    def get_unit(self):
        self.meter.write('C%d' % self.slot)
        msgin = self.meter.query('PF?')
        unit = msgin.strip().lstrip('PF')
        if unit == 'A':
            return 1
        elif unit == 'B':
            return 0
        else:
            return -1

    def parse_power(self, msg):
        msg = msg.lstrip('POD')
        #print 'parse power meter mesg',repr(msg)
        if len(msg) == 0:
            print('problem with msg', repr(msg))
            return float('nan')
        #print repr(msg)
        ch = int(msg[:2])
        status = msg[2]
        if status != 'I':
            print(('power meter status problem: ', status))
            return float('nan')
        measure = int(msg[3])
        unit = msg[4]
        if unit == 'U':
            power = 10**(old_div(float(msg[6:]), 10.)) * 1e-3
        else:
            unit = unit_dict[msg[4]]
            power = float(msg[6:]) * (10**unit)

        # unit = find_key(unit_dict,unit)
        rng = msg[5]
        rng = find_key(rng_dict, rng)
        # rng = rng_dict[msg[5]]
        return power

    def get_power(self):
        self.meter.write('C%d' % self.slot)
        msgin = self.meter.query('POD?', wait=0.1).strip().lstrip('POD')
        #print msgin
        if msgin == '':
            return float('nan')
        power = self.parse_power(msgin)
        #  Need to parse power to get the reading
        #        print "in power"
        #        print power
        #        print "return"
        return power

    def get_status(self):
        self.meter.write('C%d' % self.slot)
        start = time.time()
        #while True: # wait while zeroing
        msgin = self.meter.query('POD?').strip().lstrip('POD')
        #print 'get_status',msgin
        if len(msgin) < 2:
            msgin = 'ZZZ'
        return msgin[2]

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
        for counter in range(self.nreadings):
            w_thread = threading.Timer(1, self.wait)
            w_thread.start()
            w_thread.join()
            with self.meter.lock:
                power = self.get_power()
            self.readings.append(power)

    def measure_wait_after(self):
        for counter in range(self.nreadings):
            power = self.get_power()
            self.readings.append(power)
            if counter == self.nreadings - 1:
                break
            w_thread = threading.Timer(1, self.wait)
            w_thread.start()
            w_thread.join()

    def measure_old(self):
        #print self.nreadings
        if self.nreadings > 0:
            #threading.Timer(1.01, self.measure, [readings]).start() 
            self.nreadings -= 1
            threading.Timer(1.1, self.measure).start()
            power = self.get_power()
            #print power
            self.readings.append(power)
            #print 'measure readings',self.readings
            #print self.nreadings
    def measure2(self):
        readings = []
        for loop in range(self.nreadings):
            readings.append(self.get_power())
        self.nreadings = 0

    def read_pwm_log(self):
        #while self.nreadings>0:
        #while len(self.readings) != self.init_nreadings:
        #    time.sleep(1)
        self.measure_thread.join()
        #print 'read_pwm_log',self.readings
        return np.array(self.readings)

    def zero(self):
        start = time.time()
        self.meter.write('C%d' % self.slot)
        self.meter.write('PZ')
        # check status until zero is complete
        time.sleep(1)
        while True:
            status = self.get_status()

            if 'Z' not in status:
                break
            else:
                time.sleep(1)
        t = time.time() - start
        print('Done zero: %.2f' % (t))
        return t


if __name__ == '__main__':

    #pm = dev('dev3',10)
    pm = dev(3, '/dev/ttyUSB0', 1)
    print(pm.meter.query('OD1, S'))
    import logging
    logging.basicConfig(filename='aq2733.log', level=logging.DEBUG)
    for N in range(4000):
        logging.info(pm.meter.query('OD1, S').strip())
        time.sleep(1)
