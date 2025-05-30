from __future__ import print_function
from builtins import str
from builtins import object
#!/usr/bin/env python
import Gpib_prologix_nt_ver2 as Gpib
import time
# import ctypes
# import string
import serial

# Note that each function has a "slot" argument that is not used.
# This is to be consistent with the form of the ag8166.dev functions for
# calling an attenuator module in the Agilent 8166 box.  The Tektronix TM5003
# power box forwards its GPIB line directly to the OA5002 attenuator so a
# slot number is not necessary.


class device(object):
    def __init__(self, addr, serialport):
        """Connect to and reset a Tektronix OA5002 optical attenuator module"""
        self.port = serialport
        self.addr = addr
        self.meter = Gpib.Gpib(addr, serialport)
        self.meter.write('HEADER 0')

    def enable(self, slot=0):
        msg = 'DISABLE 0'
        self.meter.write(msg)

    def disable(self, slot=0):
        msg = 'DISABLE 1'
        self.meter.write(msg)

    def get_stat(self, slot=0):
        try:
            # for consistency with Agilent attenuators, this function needs
            # to wait until attenuator has finished adjusting to return a value
            msg = 'ADJ?'
            reading = '1\n'
            while (int(reading) == 1):
                self.meter.write(msg)
                reading = self.meter.read()
                time.sleep(0.1)
            msg = 'DISABLE?'
            self.meter.write(msg)
            reading = self.meter.read()
            if (int(reading) == 0):
                return 1
            return 0
        # except self.meter.error:
        except:
            return -1

    def set_att(self, att, slot=0):
        """Set the attenuation"""
        msg = 'ATTEN:DB %s' % (str(att))
        self.meter.write(msg)

    def set_lambda(self, wav, slot=0):
        """Set the wavelength in nm"""
        msg = 'WAV %sNM' % (str(wav))
        self.meter.write(msg)

    def get_att(self, slot=0):
        """Get the attenuation"""
        # print "hello"
        try:
            msg = 'ATTEN:DB?'
            self.meter.write(msg)
            reading = self.meter.read()
            return float(reading)
        # except self.meter.error:
        except:
            return None

    def get_lambda(self, slot=0):
        """Get the wavelength"""
        try:
            msg = 'WAV?'
            self.meter.write(msg)
            reading = self.meter.read()
            print(reading)
            return float(reading)
        # except self.meter.error:
        except:
            return None

    def close(self):
        """End communication with the DMM"""
        self.meter.loc()


if (__name__ == '__main__'):
    serialport = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.5)
    dev1 = device()
    a = dev1.get_lambda()
    print('%.2e' % a)
    dev1.close()
