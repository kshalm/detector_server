# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 11:14:35 2014

@author: qittlab
"""
from __future__ import division
from __future__ import print_function
from builtins import object
from past.utils import old_div
import Gpib
import time
"""
class dev:
    def __init__(self,addr,serialport=''):
        if isinstance(addr,str):
            self.meter = Gpib.Gpib(addr)
        else:
            self.meter = Gpib.Gpib(addr,serialport)
        meter = self.meter
"""


class dev(object):
    def __init__(self, addr, serialport=''):
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        meter = self.meter

    def identify(self):
        msg = '*IDN?'
        self.meter.write(msg)
        result = self.meter.read()
        return result

    def set_SPE_pole(self, pole):
        """
        The pole setting is defined this way to be consistenct with psy101.py
        Set the polarization to the poles of the Poincare sphere, N=1 is 0deg,
        N=2 is 45, N=3 is 90, N=4 is -45, N=5 is RHC, N=6 is LHC, and N=7 scans
        """
        if pole == 1:
            self.meter.write(':CIRC:THET 0')
            self.meter.write(':CIRC:EPS 0')
        elif pole == 2:
            self.meter.write(':CIRC:THET 90')
            self.meter.write(':CIRC:EPS 0')
        elif pole == 3:
            self.meter.write(':CIRC:THET 180')
            self.meter.write(':CIRC:EPS 0')
        elif pole == 4:
            self.meter.write(':CIRC:THET 270')
            self.meter.write(':CIRC:EPS 0')
        elif pole == 5:
            self.meter.write(':CIRC:THET 0')
            self.meter.write(':CIRC:EPS 90')
        elif pole == 6:
            self.meter.write(':CIRC:THET 0')
            self.meter.write(':CIRC:EPS -90')
        else:
            print('Input Error')
        return None

    def set_SOP_angle(self, theta, phi):
        """
        Setting the angle of the ellipse per psy101.py
        """
        twotheta = 2 * theta
        twoeps = 2 * phi
        self.meter.write(':CIRC:THET %.2f' % twotheta)
        self.meter.write(':CIRC:EPS %.2f' % twoeps)
        return None

    def get_SOP_angle(self):
        #use this to return polarization angle of the ellipse
        self.meter.write(':CIRC:THET?')
        thetareading = old_div(float(self.meter.read()), 2)
        self.meter.write(':CIRC:EPS?')
        epsilonreading = old_div(float(self.meter.read()), 2)
        return thetareading, epsilonreading

    def set_Poincare_angle(self, theta, phi):
        """
        Setting the angle on the Poincare Sphere
        """
        self.meter.write(':CIRC:THET %.2f' % theta)
        self.meter.write(':CIRC:EPS %.2f' % phi)
        return None

    def get_Poincare_angle(self):
        self.meter.write(':CIRC:THET?')
        thetareading = self.meter.read()
        self.meter.write(':CIRC:EPS?')
        epsilonreading = self.meter.read()
        return thetareading, epsilonreading

    def set_Polarizer_angle(self, theta):
        """
        Setting the angle on the Poincare Sphere
        """
        self.meter.write(':POS:POL %.2f' % theta)
        return None

    def get_Polarizer_angle(self):
        self.meter.write(':POS:POL?')
        thetareading = self.meter.read()
        return float(thetareading)

    def writeconfig(self, f):
        f.write('#Polarization controller is ' + self.identify().strip() +
                '\n')
        theta, eps = self.get_SOP_angle()
        f.write('# SOP Theta: %f\n# SOP Epsilon: %f\n' % (theta, eps))
        theta = self.get_Polarizer_angle()
        f.write('# POL Theta: %f\n' % (theta))
        return None

    def close(self):
        self.meter.close()


if __name__ == '__main__':
    pc = dev('dev6')
    import sys
    pc.set_Polarizer_angle(90)
    pc.writeconfig(sys.stdout)
