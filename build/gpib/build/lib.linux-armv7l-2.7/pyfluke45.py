from __future__ import print_function
from builtins import object
#!/usr/bin/env python
import sys, os, termios, TERMIOS, string, time


class device(object):
    def __init__(self, port=0, baud=9600, address=0):

        if (port < 0 or port > 7):
            print('Error - Bad port number %d\n' % (port))
            return None
        self.dev = '/dev/ttyUSB%d' % (port)
        self.fd = os.open(self.dev, os.O_RDWR)
        if (self.fd < 0):
            print('Error - Unable to open port \"%s\" for output\n' %
                  (self.dev))
            return None

        baudlist = [300, 1200, 2400, 4800, 9600, 19200, 38400]
        baudconstants = [
            TERMIOS.B300, TERMIOS.B1200, TERMIOS.B2400, TERMIOS.B4800,
            TERMIOS.B9600, TERMIOS.B19200, TERMIOS.B38400
        ]

        if baud not in baudlist:
            print('Error - Unsupported baud rate: %d\n' % (baud))
            return None
        baudconstant = baudconstants[baudlist.index(baud)]

        if (address < 0 or address > 15):
            print('Error - Bad address %d\n' % (address))
            return None
        self.address = address

        self.termio = termios.tcgetattr(self.fd)
        # iflag  - no input so we don't care
        self.termio[0] = 0
        # oflag  - set for raw
        self.termio[1] = 0
        # cflag
        self.termio[2] = TERMIOS.CS8 | TERMIOS.CLOCAL
        # lflag - don't need
        self.termio[3] = 0
        self.termio[4] = baudconstant
        self.termio[5] = baudconstant
        # I don't know what to do with cc for now

        termios.tcflush(self.fd, TERMIOS.TCIOFLUSH)
        termios.tcsetattr(self.fd, TERMIOS.TCSANOW, self.termio)
        self.voltage = None
        outstring = '*IDN?\n'
        result = os.write(self.fd, outstring)
        #print result
        res = os.read(self.fd, 80)
        #print res
        while string.find(res, '=>') < 0:
            res = res + os.read(self.fd, 80)
            #print res
        print(res)

    def get(self):
        outstring = 'VAL?\n'
        result = os.write(self.fd, outstring)
        #print result
        res = os.read(self.fd, 80)
        #print res
        while string.find(res, '=>') < 0:
            res = res + os.read(self.fd, 80)
        offset = string.find(res, '=>')
        res = string.atof(res[0:offset])
        #print res
        return res

    def read(self):
        res = self.get()
        return res


if __name__ == '__main__':
    port = 0
    if (len(sys.argv) > 1):
        port = string.atoi(sys.argv[1])
    vsource = device(port=port)
    ans = vsource.read()
    print(ans)
