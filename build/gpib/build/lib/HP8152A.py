from builtins import object
import serial
import Gpib_prologix_nt_ver2 as Gpib
import time


class device(object):
    def __init__(self, addr, serialport):

        # -- Add general declaration 3/3/2015 --
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        # -- end --

        #self.port = serialport
        #self.addr = addr
        #self.meter = Gpib.Gpib(addr, serialport)

    def set_lambda(self, Ch, wavelength):
        '''Ch = 1 for A, 2, for B'''
        msg = 'WVL%d,%0.3fnm' % (Ch, wavelength)
        self.meter.write(msg)

    def get_lambda(self, Ch):
        '''Get wavelength setting for Ch'''
        outmsg = 'WVL?%d' % Ch
        self.meter.write(outmsg)
        time.sleep(0.5)
        msg = self.meter.read()
        return msg

    def set_meas(self):
        '''Set the meter to MEAS mode'''
        msg = 'M2'
        self.meter.write(msg)

    def get_Pwr(self, Ch):
        '''Get power meter reading'''
        outmsg = 'M2;CH%d;ENTER' % Ch
        self.meter.write(outmsg)
        time.sleep(0.5)
        msg = self.meter.read()
        return msg
