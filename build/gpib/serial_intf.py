from __future__ import print_function
from builtins import input
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
        return eval(input('Expecting input:\n>'))

    def readline(self):
        return eval(input('Expecting input:\n>'))

    def close(self):
        pass


def serial_parse_args(addr):
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
