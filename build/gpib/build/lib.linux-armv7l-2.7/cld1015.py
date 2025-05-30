#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
from builtins import hex
from builtins import str
from past.utils import old_div
import sys, os, string, time
import threading
from laser import Laser
import usbtmc
import usb
# from copy import deepcopy
"""Thorlabs CLD1015 Laser driver."""


class dev(Laser):
    def __init__(self, device='', idVendor=4883, idProduct=32847):
        """ Written by Krister """
        super(dev, self).__init__(idVendor, idProduct)
        # These are the default values for the USB vendor and product IDs.

        self.idVendor = idVendor
        self.idProduct = idProduct

        if (idVendor == ''):
            self.idVendor = 4883

        if (idProduct == ''):
            self.idProduct = 32847

        self.meter = self.connect()
        print("Connected to:", self.identify())

    def connect(self):
        # print "IDs:", self.idVendor, self.idProduct
        instr = usbtmc.Instrument(self.idVendor, self.idProduct)

        #self.identity = instr.ask("*IDN?")
        #print "Connected to: " , self.identity
        return instr

    #   # # ahhhhhh:  dev in ag8166 needs to inherit from ojbect (i.e. class dev(object) in ag8166.py)
    #   # #print type(dev)
    #   # #print type(self)
    #   # #ag8166.dev.__init__(self,addr,serialport)
    #   # #print 'after call to super in ag81980',self.addr,self.port
    #   # if type(addr)==list:
    #   #     self.p = addr  # should I make a deepcopy here?  Not sure, will not for now
    #   #     for item in self.p:
    #   #         if item.has_key('value'):
    #   #             name = item['name']
    #   #             value = item['value']
    #   #             if 'ddress' in name:
    #   #                 gpibaddress = value
    #   #             elif 'slot' in name:
    #   #                 slot = value
    #   #     #print 'config from list addr %d, slot %d'%(gpibaddress, slot)
    #   # elif type(addr)==str:
    #   #   # The arguments are shifted by 1
    #   #   gpibaddress = int(addr.strip('dev'))
    #   #   if type(serialport)==int:
    #   #       slot = serialport
    #   # else:
    #   #   gpibaddress = addr
    #   # self.slot = slot
    #   # self.gpibaddress = gpibaddress
    #   # #print type(gpibaddress)
    #   # params[0]['value']=gpibaddress
    #   # params[1]['value']=self.slot
    #   # if not hasattr(self,'p'):
    #   #     self.p = deepcopy(params)
    def get_param(self, msgout):
        reply = self.meter.ask(msgout).strip()
        # reply = self.meter.read(100).strip()
        try:
            ret = float(reply.strip())
        except:
            errmsg = 'problem with float conversion in %s, %s' % (
                msgout, reply.strip())
            print(errmsg)
            raise Exception(errmsg)
            ret = float('NaN')
        return ret

    def set_param(self, msgout, msgcheck, value):
        self.meter.ask(msgout)
        ret = self.get_param(msgcheck)
        # if ret!=value:
        #   print 'problem with %s'%msgout
        #   raise Exception ('problem with %s'%msgout)
        #   ret = float('NaN')
        return ret

    def enable(self):
        msg1 = 'OUTP%d:STAT 1' % (self.slot)
        msg2 = 'OUTP%d:STAT?' % (self.slot)
        return self.set_param(msg1, msg2, 1)

    def brightness(self, val):
        msg1 = 'DISP:BRIG'
        msg2 = msg1 + '?'

        if (val < 0.2):
            val = 0.2

        brigh = old_div((val - 0.2), 0.8)

        brigh = str(brigh)
        # self.set_param(msg1, msg2, brigh)
        self.meter.write(msg1 + " " + brigh)
        print(self.meter.ask("DISP:BRIG?"))
        return

    def writeconfig(self, f):
        msg = self.identify()
        f.write('# ' + msg + '\n')
        f.flush()

    # def disable(self):
    #     msg1 = 'OUTP%d:STAT 0'%(self.slot)
    #     msg2 = 'OUTP%d:STAT?'%(self.slot)
    #     return self.set_param(msg1, msg2, 0)

    # def get_lambda(self):
    #   try:
    #     msg = ':SOUR%s:WAV?'%(str(self.slot))
    #     self.meter.ask(msg)
    #     self.wl = float(self.meter.read().strip())
    #     return self.wl
    #   except:
    #     return float('NaN')
    # def set_lambda(self,wl):
    #   #try:
    #     msg = ':SOUR%d:WAV %fE-9'%(self.slot,wl)
    #     self.meter.ask(msg)
    #     self.wl = self.get_lambda()*1e9
    #     return self.wl
    #   #except:
    #   #  return float('NaN')
    # def get_power(self):
    #   try:
    #     msg = ':SOUR%s:POW?'%(str(self.slot))
    #     self.meter.ask(msg)
    #     self.power = float(self.meter.read().strip())
    #     return self.power
    #   except:
    #     return float('NaN')
    # def set_power(self,value):
    #   try:
    #     msg = ':SOUR%d:POW %f'%(self.slot,value)
    #     self.meter.ask(msg)
    #     self.power = self.get_power()
    #     if value != self.power:
    #   print 'Problem setting laser power to %f'%(value)
    #   self.power = float('NaN')
    #     return self.power
    #   except:
    #     return float('NaN')

    def identify(self):
        msg = '*IDN?'
        self.identity = self.meter.ask(msg)
        return self.identity

    # #def identify(self):
    # #  return self.identify_slot(self.slot)
    # def writeconfig(self,f):
    #   msg = self.identify()
    #   wl = self.get_lambda()
    #   power = self.get_power()
    #   f.write(msg)
    #   f.write('# wavelength: %e\n# power: %f\n'%(wl,power))
    #   f.flush()
    # def close(self):
    #   self.meter.close()


if __name__ == '__main__':
    # find USB devices
    devices = usb.core.find(find_all=True)
    # loop through devices, printing vendor and product ids in decimal and hex
    for cfg in devices:
        sys.stdout.write('Decimal VendorID=' + str(cfg.idVendor) +
                         ' & ProductID=' + str(cfg.idProduct) + '\n')
        sys.stdout.write('Hexadecimal VendorID=' + hex(cfg.idVendor) +
                         ' & ProductID=' + hex(cfg.idProduct) + '\n\n')

    laser = dev()
    print(" ")
    print('lambda', laser.get_lambda())
    #print laser.get_power()
    #print laser.set_power(0.004)
    #print laser.identify()
    #laser.writeconfig(sys.stdout)
