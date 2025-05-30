from __future__ import print_function
from builtins import object
#!/usr/bin/env python
import Gpib
import string

# simple driver for 8505
# by default read method gets resistance - can read other stuff
# sometimes the read doesn't return anything - in this case we try again


class device(object):
    def __init__(self, name):
        self.dev = Gpib.Gpib(name)
        self.read()

    def read(self):
        self.dev.write("?")
        result = self.dev.read()
        floatresult = string.atof(string.strip(result))
        return floatresult

#     return 0.0

    def close(self):
        self.dev.close()

if (__name__ == '__main__'):
    fl = device('dev10')
    a = fl.read()
    print(a)
    fl.close()
