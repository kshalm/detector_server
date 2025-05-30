# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 08:25:55 2015

@author: qittlab
"""
from __future__ import print_function

import serial
import time


def query(s, msg):
    s.write(msg + '\n')
    #time.sleep(.1)
    print(msg, repr(s.read(100)))


s = serial.Serial('COM7', 115200, timeout=0.1)
"""
query(s,'++addr')
query(s,'++eoi')
query(s,'++auto')
query(s,'++eos')
query(s,'++savecfg')

s.write('++auto 0\n')
"""
s.write('++rst\n')
time.sleep(1)
query(s, '++ver')
query(s, '++addr')
s.write('++ifc\n')

s.close()
