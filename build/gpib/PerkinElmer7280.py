from __future__ import print_function
from builtins import range
from builtins import object
#!/usr/bin/env python
import Gpib
import string

# simple driver for perkin elmer lockin 
# by default read method gets resistance - can read other stuff
# sometimes the read doesn't return anything - in this case we try again


class device(object):
    def __init__(self, addr, serialport=''):

        # -- Add general declaration 3/3/2015 --
        self.meter, self.addr, self.port, self.p = Gpib.Gpib2(addr, serialport)
        self.dev = self.meter
        # -- end --

        #self.dev = Gpib.Gpib(name)

    def read(self, meas='R'):
        meas = string.upper(meas)
        getcommand = {'R': 'MAG.', 'X': 'X.', 'Y': 'Y.'}
        try:
            self.dev.write(getcommand[meas])
            for i in range(3):  #three strikes and you are out 
                instring = string.strip(self.dev.read())
                if len(instring) > 0: break
                # seems we didn't get anything, try again
                if i == 2: return 0  # I should really throw an error here
                self.dev.write(getcommand[meas])
        except self.dev.error:
            return None

        #(val,unit,meastype)=string.split(instring)
        #if meastype != meas : print 'error in measurement type'
        #if unit[0]=='K': mult=1000.0
        #elif unit[0]=='M': mult=1.0e-3
        #elif unit[0]=='U': mult=1.0e-6
        #else: mult=1.0
        #floatval = string.atof(val)*mult
        floatval = string.atof(instring)
        return (floatval)

    def close(self):
        self.dev.close()


if (__name__ == '__main__'):
    lr = device('dev15')
    a = lr.read()
    print(a)
    lr.close()
