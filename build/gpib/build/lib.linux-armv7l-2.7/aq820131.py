from __future__ import division
from past.utils import old_div
import aq820133
import Gpib
import threading
import time
import string
import numpy as np
import math

params = [
    {
        'name': 'AQ8201-110 GPIB Address',
        'type': 'int',
        'limits': (1, 32),
        'value': 4
    },
    {
        'name': 'AQ8201-110 Slot',
        'type': 'int',
        'values': {1, 2, 3, 5, 6, 7, 8, 9, 10},
        'value': 3
    },
]


class dev(aq820133.dev):
    def set_att(self, value):
        #  Need to round to nearest 0.05
        value = old_div(round(value * 2., 1), 2.0)
        return super(dev, self).set_att(value)
