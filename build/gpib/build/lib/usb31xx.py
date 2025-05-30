# -*- coding: utf-8 -*-
#
# 
"""
Demonstrates how items may trigger callbacks when activated
"""
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import dict
from builtins import range
from builtins import str
from builtins import bytes
from builtins import chr
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import object

###############################################################################
import hid
import time
import struct


def list_devices():
    devices = []
    l = hid.enumerate(0, 0)
    for item in l:
        if item['vendor_id'] == 0x9db:
            devices.append(item)
    return devices


class usb31xx(object):
    def __init__(self,
                 interval=1,
                 average=5,
                 printOutput=False,
                 devId=0x009c,
                 path=None):
        self.hex_codes()
        self.printCommands = printOutput  #allow printing of messages
        self.printStatus = printOutput
        self.print_msgs('s', "Opening device")
        # try to set devId... check if path is used not devId
        if path is not None:
            devices = list_devices()
            for item in devices:
                if item['path'] == path:
                    devId = item['product_id']
                    #print 'setting dev_Id to %d'%devId
        self.devId = devId
        self.NUMCH = 8
        if devId == 0x9e:
            self.NUMCH = 16
        try:
            if path is None:
                self.HIDid = hid.device(
                    0x09db, self.devId)  #open device for further commands
            else:
                self.HIDid = hid.device(
                    0x09db, self.devId,
                    path=path)  #open device for further commands

        except IOError as ex:
            try:
                self.devId = 0x009d
                if path is None:
                    self.HIDid = hid.device(
                        0x09db, self.devId)  #open device for further commands
                else:
                    self.HIDid = hid.device(
                        0x09db, self.devId,
                        path=path)  #open device for further commands
                #self.HIDid = hid.device(0x9db, 0x009d)     #open device for further commands
            except IOError as ex:
                print(ex)
                print(
                    "You probably don't have the hard coded test hid. Update the hid.device line"
                )
                print(
                    "in this script with one from the enumeration list output above and try again."
                )
        #print 'HIDid',self.HIDid    
        self.print_msgs(
            's', "Manufacturer: %s" %
            self.HIDid.get_manufacturer_string())  #obtain device information
        self.print_msgs(
            's', "Product: %s" %
            self.HIDid.get_product_string())  #obtain device information
        self.print_msgs(
            's', "Serial No: %s" %
            self.HIDid.get_serial_number_string())  #obtain device information
        self.bipolar = 1
        self.USB31xx_readMemoryFlash()  #get calibration for analouge outputs

    def hex_codes(self):
        self.hCode = dict()
        self.hCode['DIO_DIR_OUT'] = 0x00
        self.hCode['DIO_DIR_IN'] = 0x01

        self.hCode['BLINK'] = 0x40
        self.hCode['DCONFIG'] = 0x01  #Configure digital port
        self.hCode[
            'DCONFIG_BIT'] = 0x02  #Configure individual digital port bits
        self.hCode['DIN'] = 0x03  #Read digital port
        self.hCode['DOUT'] = 0x04  #Write digital port
        self.hCode['DBIT_IN'] = 0x05  #Read digital port bit
        self.hCode['DBIT_OUT'] = 0x06  #Write digital port bit

        self.hCode['AOUT'] = 0x14  #Write analog output channel
        self.hCode['AOUT_SYNC'] = 0x15  #Synchronously update outputs
        self.hCode['AOUT_CONFIG'] = 0x1C  #Configure analog output channel
        self.hCode['MEM_READ'] = 0x30  # Read Memory

        self.hCode['CINIT'] = 0x20  #Initialize Counter
        self.hCode['CIN'] = 0x21  #Read Counter

    def print_msgs(self, msgType, msg):
        if self.printCommands and msgType == 'c':
            print(msg)
        if self.printStatus and msgType == 's':
            print(msg)

    def USB31xx_blink(self, nBlinks):
        self.print_msgs('c', 'blink %r times' % nBlinks)
        self.HIDid.write([self.hCode['BLINK'], nBlinks])

    def USB31xx_Dout(self, value):
        self.print_msgs('c', 'writing digital port: %r' % value)
        self.HIDid.write([self.hCode['DCONFIG'], self.hCode['DIO_DIR_OUT']])
        self.HIDid.write([self.hCode['DOUT'], value])

    def USB31xx_Din(self, value):
        self.print_msgs('c', 'reading digital port: %r' % value)
        self.HIDid.write([self.hCode['DCONFIG'], self.hCode['DIO_DIR_IN']])
        self.HIDid.write([self.hCode['DIN'], value])
        status = self.HIDid.read(2)[1]
        return status

    def USB31xx_Aout(self, port, aVolt):
        port = int(float(port))
        self.print_msgs('c', 'set voltage on port %r to %r V' % (port, aVolt))
        if self.bipolar == 0:
            aVolt = int(aVolt / 10.0 * 256 * 256)  #convert voltage to range
            aVolt = int(self.slope[port] * aVolt +
                        self.offset[port])  #apply calibration
            highBit, lowBit = divmod(aVolt, 256)  #split into 2 bits
        else:
            aVolt = int((aVolt / 10.) * (2.**15) + 2.**15)
            aVolt = int(self.slope[port] * aVolt +
                        self.offset[port])  #apply calibration
            if aVolt > 0xFFFF:
                aVolt = 0xFFFF
            elif aVolt < 0:
                aVolt = 0
            highBit, lowBit = divmod(aVolt, 256)  #split into 2 bits
        #print 'highbit, lowbit, %x %x'%(highBit, lowBit)
        self.HIDid.write([self.hCode['AOUT_CONFIG'], port, self.bipolar
                          ])  #configure port for output
        self.HIDid.write(
            [self.hCode['AOUT'], port, lowBit, highBit, 0])  #set voltage

    def USB31xx_Aout_all(self, aVolt=0.0):
        for port in range(0, self.NUMCH):
            self.USB31xx_Aout(port, aVolt)

    def USB31xx_InitCounter(self):  #initializes counter and sets to zero
        self.HIDid.write([self.hCode['CINIT']])

    def USB31xx_ReadCounter(self):  #read current value from counter
        self.HIDid.write([self.hCode['CIN'], 1])
        mccoutput = self.HIDid.read(5)[1:5]
        print(mccoutput)
        counter = mccoutput[0] | (mccoutput[1] << 8) | (mccoutput[2] << 16) | (
            mccoutput[3] << 24)
        return counter

    def msgScrub(self, msg):
        msg = msg.replace('[', '')
        msg = msg.replace(' ', '')
        msg = msg.replace(']', '')
        msg = msg.replace('\'', '')
        msg = msg.replace(',', ' ')
        return msg

    def USB31xx_readMemoryFlash(self):
        ### reads and returns the slope and offset calibration data 
        ### for the USB3103/USB3104  analouge outputs
        self.print_msgs('s', 'loading analoge data from device')
        l = []  #initialise empty aray
        stAddress = 0x100 + 8 * self.bipolar  #start location of calibration data
        for x in range(0, self.NUMCH):  #for each analouge output
            adr = stAddress + x * 0x10  #address to read from
            highBit, lowBit = divmod(
                int(adr), 255
            )  # device can only read small bits at a time, so divide into 2 bits
            # infom device that you want to read from memory, at a certain address, and so many bytes
            self.HIDid.write(
                [self.hCode['MEM_READ'], lowBit, highBit, 0x0, 16])
            time.sleep(0.1)  #wait 0.1 seconds
            msg = self.msgScrub(
                str(self.HIDid.read(16))
            )  # read from memort and turn to string, remove characters from msg, replace(,) with space
            for y in msg.split(
            ):  # split message into chuncks, then for each chunk
                try:  # attept to
                    l.append(y)  # append chunk into an array
                except ValueError:  # if append operation fails
                    pass  # do  nothing 

        self.slope = [0.0] * self.NUMCH  #initialise slope array
        self.offset = [0.0] * self.NUMCH  #initialise ofset array
        for x in range(0, self.NUMCH):  # Once for each output
            adr = x * 16  # there are 16 bytes of information for each output
            for y in range(
                    0, 5, 4
            ):  # y = 0,4. 0 for the adress of slopes, 4 for the addess of offsets
                floatPack = ''  # create empty string
                for z in range(0, 4):  # read through 4 consecutive adresses
                    a = bytes(chr(int(l[adr + y + z]))
                              )  #turn string > integer > character > byte
                    floatPack = floatPack + a  #add byte to byte string
                #unpack a 4 byte string into a tupple, convert to string then remove characters         
                floatStr = str(struct.unpack('f', floatPack)).strip(',()')
                if y == 0:  #add float to slope configuratiom
                    self.slope[x] = float(floatStr)
                elif y == 4:  #add float to offset configuratiom
                    self.offset[x] = float(floatStr)
        self.print_msgs('s', 'loaded slopes and offsets')

    def close(self):
        self.print_msgs('s', "Closing device")
        self.HIDid.close()


##############################################################################    

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', type=int, default=0, help='channel number')
    parser.add_argument('-v', type=float, default=0, help='voltage out')

    args = parser.parse_args()

    print('setting channel %d to %f' % (args.c, args.v))

    vsrc = usb31xx()

    vsrc.USB31xx_Aout(args.c, args.v)
    vsrc.close()
