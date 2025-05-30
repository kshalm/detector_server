#!/usr/bin/env python
from __future__ import division
from past.utils import old_div
import math


def RtoT(res):
    # should I go a little lower?
    if res < 1000.0: res = 1000.0
    # this is 10 volts out of the bridge    
    if res > 200000.0: res = 200000.0
    return pow((old_div(2.85, math.log(old_div((res - 652.0), 100.0)))), 4.0)
