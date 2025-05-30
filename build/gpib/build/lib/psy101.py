#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
from builtins import object
from past.utils import old_div
from Gpib import *
import time
import ctypes
import string
import serial, serial_intf
import numpy as np
"""

class dev:
  def __init__(self, COMport):
    port = '\\\\.\\COM%d'%COMport
    self.pol = serial.Serial(port=port, baudrate=115200,timeout=1);
    self.pol.close()
"""


class dev(object):
    def __init__(self, COMport):
        port, self.p = serial_intf.serial_parse_args(COMport)
        if port == 'fake':
            self.pol = serial_intf.fake()
        else:
            self.pol = serial.Serial(port=port, baudrate=115200, timeout=1)
        self.pol.close()
        self.port = port

    def identify(self):  #ID the polarizer
        self.pol.open()
        self.pol.write('*IDN?')
        result = self.pol.readline()
        self.pol.close()
        return result

    def version(self):  #firmware version
        self.pol.open()
        self.pol.write('*VER?')
        result = self.pol.readline()
        self.pol.close()
        return result

    def get_pow(self):  #get input power (dBm)
        self.pol.open()
        self.pol.write('*POW?')
        result = self.pol.readline()
        self.pol.close()
        return result

    def set_lambda(self, wavelength):  #set wavelength, range = 1500-1600
        self.pol.open()
        self.pol.write('*WAV %d#' % wavelength)
        result = self.pol.readline()
        self.pol.close()
        return result

    def get_lambda(self):  #get wavelength
        self.pol.open()
        self.pol.write('*WAV?')
        result = float(self.pol.readline().strip('#').lstrip('*'))
        self.pol.close()
        return result

    def set_SPE_mode(self):  #set mode for determining polarization max
        self.pol.open()
        self.pol.write('*MOD:SPE#')
        result = self.pol.readline()
        self.pol.close()
        return result

    def set_ANG_mode(self):  #set mode for defining polarization
        self.pol.open()
        self.pol.write('*MOD:ANG#')
        result = self.pol.readline()
        self.pol.close()
        return result

    def set_SOP_angle(self, theta, phi):  #polarization angles in degrees
        self.pol.open()
        # theta has to be between 0 and 180 degrees
        # phi has to be between -45 and 45 degrees
        theta = np.mod(theta, 180.0)
        if abs(phi) > 45:
            print(
                'Trying to set phi in PSY-101 to a number >45 or <-45 degrees: %f'
                % (phi))
        self.pol.write('*SOP:THA %.2f#' % theta)
        self.pol.write('*SOP:PHI %.2f#' % phi)
        self.pol.write('*SOP:ENA ON#')
        self.pol.write('*MOD:ANG#')
        result = self.pol.readline()
        self.pol.close()
        return result

    def get_SOP_angle(self):
        self.pol.open()
        self.pol.write('*SOP:ANG#')
        self.pol.write('*SOP?')
        a = self.pol.readline()
        if 'E09' in a:
            theta = 720
            epsilon = 720
        else:
            theta = float(a.split(',')[0].split(' ')[1])
            epsilon = float(a.split(',')[1].split(' ')[1].rstrip('#'))
        self.pol.close()
        return theta, epsilon

    def set_Poincare_angle(self, theta, phi):
        self.pol.open()
        #msg1='*SOP:THA %.2f#'%(theta/2.0)
        #msg2='*SOP:PHI %.2f#'%(phi/2.0)
        self.pol.write('*SOP:THA %.2f#' % (old_div(theta, 2.0)))
        self.pol.write('*SOP:PHI %.2f#' % (old_div(phi, 2.0)))
        self.pol.write('*SOP:ENA ON#')
        self.pol.write('*MOD:ANG#')
        result = self.pol.readline()
        self.pol.close()
        return result

    def get_Poincare_angle(self):
        self.pol.open()
        self.pol.write('*SOP:ANG#')
        self.pol.write('*SOP?')
        a = self.pol.readline()
        if 'E09' in a:
            twotheta = 720
            twoepsilon = 720
        else:
            twotheta = 2 * float(a.split(',')[0].split(' ')[1])
            twoepsilon = 2 * float(a.split(',')[1].split(' ')[1].rstrip('#'))
        self.pol.close()
        return twotheta, twoepsilon

    def set_SPE_pole(self, pole):
        #Set the polarization to the poles of the Poincare sphere, N=1 is 0deg,
        #N=2 is 45, N=3 is 90, N=4 is -45, N=5 is RHC, N=6 is LHC, and N=7 scans
        self.pol.open()
        self.pol.write('*SPE:STA %d#' % pole)
        result = self.pol.readline()
        self.pol.close()
        return result

    def writeconfig(self, f):
        f.write('#Polarization controller is ' + self.identify() + '\n')
        f.write('#Poincare Angles are set to 2theta = %f, 2epsilon = %f\n' %
                (float(self.get_Poincare_angle()[0]),
                 float(self.get_Poincare_angle()[1])))
        f.write('#Polarizer Wavelength: %f\n' % (self.get_lambda()))
        return None

    def close(self):
        self.pol.close()


if (__name__ == '__main__'):
    dev1 = dev(9)
    a = dev1.get_route()
    print('%d' % a)
    dev1.close()
