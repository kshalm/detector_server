from __future__ import print_function
from builtins import object
#!/usr/bin/env python
import time
import ctypes
import string
import serial
import os, sys, re
import serial_intf
if os.name == 'posix':
    import usb

USB_PORTS_STR = '^\s*(\d+)-(\d+(?:\.\d+)*)'
CALIB_LINE_STR = USB_PORTS_STR +\
    '\s*:\s*scale\s*=\s*([+|-]?\d*\.\d+)\s*,\s*offset\s*=\s*([+|-]?\d*\.\d+)'
USB_SYS_PREFIX = '/sys/bus/usb/devices/'


def readattr(path, name):
    """
    Read attribute from sysfs and return as string
    """
    try:
        f = open(USB_SYS_PREFIX + path + "/" + name)
        return f.readline().rstrip("\n")
    except IOError:
        return None


def find_attr(device, name):
    bus_id = device.bus
    dev_id = device.address
    for dirent in os.listdir(USB_SYS_PREFIX):
        matches = re.match(USB_PORTS_STR + '$', dirent)
        if matches:
            bus_str = readattr(dirent, 'busnum')
            if bus_str:
                busnum = float(bus_str)
            else:
                busnum = None
            dev_str = readattr(dirent, 'devnum')
            if dev_str:
                devnum = float(dev_str)
            else:
                devnum = None
            if busnum == bus_id and devnum == dev_id:
                attr_str = readattr(dirent, name)
                return attr_str


def get_serialnumber():
    if os.name == 'nt':
        # need to figure out which comport incase there are multiple switches
        import win32com.client
        wmi = win32com.client.GetObject("winmgmts:")
        devices = wmi.InstancesOf("Win32_USBHub")
        for dev in devices:
            if 'OSWxx' in dev.Name:
                #print dev.DeviceID
                return dev.DeviceID
        #for a in devices[1].Properties_:
        #    print a.name, a.value:
    if os.name == 'posix':
        d = usb.core.find(idVendor=0x1313)
        #print 'd: ', d
        return find_attr(d, 'serial')

    return None


SN = get_serialnumber()


class dev(object):
    def __init__(self, COMport):
        port, self.p = serial_intf.serial_parse_args(COMport)
        if port == 'fake':
            self.sw = serial_intf.fake()
        else:
            self.sw = serial.Serial(port=port, baudrate=115200, timeout=1)
        self.sw.close()
        self.port = port

    def get_stat(self, slot):
        sw = self.get_route()
        if (sw < 1):
            return -1
        return 0

    def get_route(self, *args):  # changed arguments
        try:
            self.sw.open()
            self.sw.write('S?\n')
            time.sleep(0.01)
            a = self.sw.readline()
            a = int(a)
            self.sw.close()
            return a
        except:
            return -1

    #def route(self,slot,channel,port):
    # Arguments defined this way for consistency with AG8166 structure
    #   This is a hack... Should subclss the ag8166...
    def route(self, *args):
        port = args[-1]  # choose last argument to fix hack described above
        self.sw.open()
        self.sw.write('S %d\n' % port)
        time.sleep(0.01)
        self.sw.close()
        value = self.get_route()
        if value != port:
            print('problem setting OSW12 to %i' % port)

    def set_route(self, slot, channel, port):
        self.route(port)
        time.sleep(0.1)

    def close(self):
        self.sw.close()

    def writeconfig(self, f, *args):
        f.write('#  OSW12 switch\n')
        f.write('#  serialnumber:%s\n' % SN)
        f.write('#  serialport: %s\n' % self.port)


if (__name__ == '__main__'):
    print("Serial Num: ", get_serialnumber())
    #dev1 = dev('fake')
    dev1 = dev('/dev/ttyUSB1')
    a = dev1.get_route()
    print('Route: %d' % a)
    dev1.route(a)
    #dev1.route(0,'a',2)
    dev1.close()
    dev1.writeconfig(sys.stdout)
