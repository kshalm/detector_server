from builtins import object
#!/usr/bin/env python
import sys, os, string, time
import threading


class Laser(object):
    def __init__(self, addr, serialport='', slot=2):
        """ Written by SaeWoo and Jeff """
        # super(Laser, self).__init__(addr,serialport)

    def connect(self, addr='', serialport=2):
        pass

    def get_param(self, msgout):
        pass

    def set_param(self, msgout, msgcheck, value):
        pass

    def enable(self):
        pass

    def disable(self):
        pass

    def get_lambda(self):
        pass

    def set_lambda(self, wl):
        #try:
        pass

    def get_power(self):
        pass

    def set_power(self, value):
        pass

    def identify(self):
        pass

    def writeconfig(self, f):
        pass

    def close(self):
        pass


# if __name__ == '__main__':
#   laser = dev('dev10',1)
#   print laser.get_lambda()
#   print laser.get_power()
#   print laser.set_power(0.004)
#   #print laser.identify()
#   import sys
#   laser.writeconfig(sys.stdout)
