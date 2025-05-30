from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import input
from future import standard_library
standard_library.install_aliases()
from builtins import object
import os


class fake(object):
    def __init__(self, *args, **kwargs):
        print('args', args)
        print('kwargs', kwargs)

    def open(self):
        pass

    def write(self, msg):
        print(msg.strip())

    def read(self):
        return eval(input('Expecting input'))

    def readline(self):
        return eval(input('Expecting input'))

    def close(self):
        pass


def list_ports():
    if os.name == 'posix':
        import usb.core
        devices = usb.core.find(find_all=True)
        devlist = []
        for d in devices:
            devlist.append('vid:pid  %X:%X' % (d.idVendor, d.idProduct))
        return devlist

    if os.name == 'nt':
        import win32com.client
        devlist = []
        wmi = win32com.client.GetObject("winmgmts:")
        for usb in wmi.InstancesOf("Win32_USBHub"):
            #print usb.DeviceID
            devlist.append(usb.DeviceID)
        return devlist


#  The method below needs to changed
def usb_parse_args(addr):
    p = None
    if type(addr) == list:
        p = addr  # should I make a deepcopy here?  Not sure, will not for now
        for item in p:
            if 'value' in item:
                name = item['name']
                value = item['value']
                if 'ddress' in name:
                    gpibaddress = value
                elif 'interface name' in name:
                    portname = value
                    serialport = portname
                elif 'interface type' in name:
                    gpibtype = value

        print('config from list addr %d, intf name %s, type %d' %
              (gpibaddress, portname, gpibtype))
        addr = gpibaddress
        if gpibtype == 4:  # this is serial
            serialport = portname
        elif gpibtype == 3:  # this is fake
            serialport = 'fake'
            print('Need to implement a fake device')
        else:  # not a valid type
            serialport = 'error'
            raise NameError("Bad configuration for the serial port")
    elif os.name == 'nt' and type(addr) == int:  # on windows machine
        serialport = '\\\\.\\COM%d' % addr
    elif isinstance(addr, str):  # string is the name of the serial port 
        serialport = addr
    port = serialport
    return port, p
