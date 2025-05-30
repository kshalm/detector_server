from __future__ import division
from __future__ import print_function
from builtins import str
from builtins import range
from builtins import object
from past.utils import old_div
import serial
import serial_intf
import binascii
import time
import struct
import threading
import math
import scipy.constants

#Serial number CRTNE4C02W:
#C-band
#Freq range = 192.5-196.25 (THz) 


class dev(object):
    #def __init__(self,port = '/dev/ttyUSB0'):
    def __init__(self, *args, **kwargs):
        port, self.p = serial_intf.serial_parse_args(args[0])

        if port == 'fake':
            self.s = serial_intf.fake()
        else:
            self.s = serial.Serial(port=port, baudrate=9600, timeout=1)
        # self.sw.close()   # Need to open and close before sending each command
        self.port = port

    def calcBIP4(self, data):
        bip8 = (data[0] & 0x0f) ^ data[1] ^ data[2] ^ data[3]
        bip4 = ((bip8 & 0xf0) >> 4) ^ (bip8 & 0x0f)
        return bip4

    def strip_str(self, x):
        return "".join([i for i in x if 31 < ord(i) < 127])

    def addBIP4(self, data):
        bip4 = self.calcBIP4(data)
        data[0] = data[0] | (bip4 << 4)
        return data

    def nop(self):
        msg = bytearray([0x00, 0x00, 0x00, 0x00])
        ret = self.send(msg)
        print(ret)

    def identity(self):
        devType = self.strip_str(self.getstring(0x01))
        manufacturer = self.strip_str(self.getstring(0x02))
        model = self.strip_str(self.getstring(0x03))
        serNum = self.strip_str(self.getstring(0x04))
        return devType, manufacturer, model, serNum

    def identify(self):
        return self.identity()

    def writeconfig(self, f):
        msg = self.identity()
        power = self.get_power()
        wl = self.get_lambda()
        f.write('# Device Type: %s\n' % msg[0])
        f.write('# Manufacturer: %s\n' % msg[1])
        f.write('# Model: %s\n' % msg[2])
        f.write('# Serial No: %s\n' % msg[3])
        f.write('# Power: %f mW\n' % power)
        f.write('# Lambda: %f\n' % wl)

    def getsetpow(self):
        msg = bytearray([0x00, 0x31, 0x00, 0x00])
        ret = self.send(msg)
        output = struct.unpack('>BBH', ret)
        power = output[2]
        #power= (ret[2]<<8) + ret[3] 
        #print power
        return power

    def get_power(self):
        ret = self.testread(0x42)  # optical power setting
        output = struct.unpack('>BBH', ret)
        power = output[2]
        #power= (ret[2]<<8) + ret[3] 
        #print power
        return old_div(power, 100.0)

    def get_temp(self):
        ret = self.readshort(0x43)
        #print ret
        return old_div(ret, 100.0)

    def set_power(self, value):
        powin = int(value * 100 * 1000)
        low = powin & 0xFF
        high = (powin & 0xFF00) >> 8
        msg = bytearray([0x01, 0x31, high, low])
        ret = self.send(msg)

    def enable(self):
        msg = bytearray([0x01, 0x32, 0x00, 0x08])
        try:
            ret = self.send(msg)
        except:
            pass

    def disable(self):
        msg = bytearray([0x01, 0x32, 0x00, 0x00])
        ret = self.send(msg)

    def testread(self, cmd):
        msg = bytearray([0x00, cmd, 0x00, 0x00])
        ret = self.send(msg)
        return ret

    def readshort(self, cmd):
        ret = self.testread(cmd)  # optical power setting
        output = struct.unpack('>BBH', ret)
        short = output[2]
        return short

    def getstring(self, cmd):
        msgin = bytearray(self.testread(cmd))
        length = 0xff & msgin[3]
        msg = []
        for i in range(old_div(length, 2)):
            msgin = bytearray(self.testread(0x0b))
            msg.append(msgin[2])
            msg.append(msgin[3])
        #print msg
        msg = str(bytearray(msg))
        #print msg
        return msg

    def getints(self, cmd):
        msgin = bytearray(self.testread(cmd))
        length = 0xff & msgin[3]
        msg = []
        for i in range(old_div(length, 2)):
            msgin = (self.testread(0x0b))
            output = struct.unpack('>BBh', msgin)
            short = output[2]
            msg.append(short)
            #msg.append(msgin[2])
            #msg.append(msgin[3])
        return msg

        #New funtions 1/29/2015

    def getch(self):
        return self.readshort(0x30)

    def setch(self, ch):
        low = ch & 0xFF
        high = (ch & 0xFF00) >> 8
        msg = bytearray([0x01, 0x30, high, low])
        ret = self.send(msg)
        return ret

    def get_wl(self, first, second):
        freqThz = self.readshort(first)
        freqGhz = self.readshort(second)
        freqHz = (freqThz + old_div(freqGhz, 1E4)) * 1E12
        msg = (old_div(scipy.constants.c, freqHz)) * 1E9
        return msg

    def get_ff(self):
        wl = self.get_wl(0x52, 0x53)
        return wl

    def get_lf(self):
        wl = self.get_wl(0x54, 0x55)
        return wl

    def get_lambda(self):
        freqThz = self.readshort(0x35)
        freqGhz = self.readshort(0x36)
        freqHz = (freqThz + old_div(freqGhz, 1E4)) * 1E12
        msg = (old_div(scipy.constants.c, freqHz)) * 1E9
        return msg

    def set_lambda(self, lamb):
        # Get 1st and 2nd ch. frequency. We want "integer" in THz and "fraction" GHz*10)  
        fraction, integer = math.modf(
            old_div(scipy.constants.c, (
                lamb * 1E3)))  #Recive lambda in nm but we want THz -> /1E3

        # Set 1st ch. freq. and send msg
        low1 = int(integer) & 0xFF
        high1 = (int(integer) & 0xFF00) >> 8
        msg1 = ([0x01, 0x35, high1, low1])
        ret1 = self.send(msg1)
        # Set 2nd ch. freq. and send msg
        low2 = int(fraction * 1E3 * 10) & 0xFF
        high2 = (int(fraction * 1E3 * 10) & 0xFF00) >> 8
        msg2 = ([0x01, 0x36, high2, low2])
        ret2 = self.send(msg2)
        return ret1, ret2

    def send(self, msg):
        self.addBIP4(msg)
        #print 'write hex: ',binascii.hexlify(msg) 
        while True:
            self.s.write(msg)
            msgin = self.s.read(4)
            if len(msgin) == 4:
                break
            print('trying again')
        #if len(msgin) != 4:
        #  raise Exception('read back wrong number of bytes %d'%len(msgin))
        #else:
        checksum = self.calcBIP4(bytearray(msgin))
        #print checksum, ord(msgin[0])>>4
        #print 'read  hex: ',binascii.hexlify(msgin)
        if checksum != ord(msgin[0]) >> 4:
            raise Exception('Checksum on msg back does not match')

        #  Should check msg[0] for error/retcode... Not sure where to do this most
        # efficiently ... here??  Only on retcode==1 is done below

        if (msg[0] & 0x01 == 1):
            # check read back on write
            good = True
            for i in range(3):
                good = good and (msg[i + 1] == ord(msgin[i + 1]))
            if not good:
                raise Exception('Error on writing message')
        return (msgin)

    def close(self):
        self.s.close()


if __name__ == '__main__':
    laser = dev('/dev/ttyUSB2')
    laser.nop()
    laser.set_power(0.001)
    print(laser.getsetpow())
    print(laser.get_power())
    try:
        # enable commands sends back extra stuff... raises an exception
        #  need to read the manual in detail to see why...
        laser.enable()
    except:
        pass
    time.sleep(3)
    print(laser.get_power())
    laser.disable()
    laser.testread(0x35)  # THz part of first ch freq
    laser.testread(0x40)
    laser.testread(0x36)  # GHz part of first ch freq 
    laser.testread(0x41)
    '''
  laser.getstring(0x01) # dev type
  laser.getstring(0x02) # manufacturer
  laser.getstring(0x03) # model 
  laser.getstring(0x04) # serial number
  laser.getstring(0x05) # mfg date
  laser.getstring(0x06) # firmware 
  laser.getstring(0x57) # currents
  laser.getstring(0x58) # temperatures
  #added info
  print laser.getstring(0X55) # last frequency
  '''
    print(laser.getints(0x58))
    print(laser.getints(0x57))
    laser.testread(0x22)  # threshold fatal condition
    laser.testread(0x23)  # theshold warning condition
    print("min power",
          repr(laser.testread(0x50)))  # min possible optical power
    print(laser.readshort(0x50))
    print("max power ",
          repr(laser.testread(0x51)))  # max possible optical power
    print(laser.readshort(0x51))
    #laser.testread(0x43) # current temperature
    print(laser.get_temp())
    laser.enable()
    f = open('test_laser.log', 'w')

    def update():
        threading.Timer(2, update).start()
        power = laser.get_power()
        out = '%.2f \t %.2f' % (time.time(), power)
        print(out)
        print("Hi")
        print(laser.getints(0x58))
        print(laser.getints(0x57))
        f.write(out + '\n')
        f.flush()

    update()

    #laser.close()
"""
print '%x'%calcBIP4(bytearray([0x01, 0x31, 0x03, 0xe8]))
d = bytearray([0x01, 0x35, 0x00, 0xC1])
print '%x'%calcBIP4(d)
addBIP4(d)
print '%x'%(d[0])
"""
