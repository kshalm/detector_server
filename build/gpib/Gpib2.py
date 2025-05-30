from __future__ import print_function
from builtins import object
import os, sys, ctypes
#from ctypes import *

gpib = getattr(ctypes.windll, "gpib-32")

RQS = (1 << 11)
SRQ = (1 << 12)
TIMO = (1 << 14)


class Gpib2(object):
    def __init__(self, addr=0, board=0):
        shortArray2 = 2 * ctypes.c_ushort
        alist = shortArray2(addr, 0xFFFF)
        self.alist = alist
        self.board = board
        self.addr = addr
        ret = gpib.EnableRemote(0, alist)
        print("init: %d" % ret)
        #self.error = gpib.error

    def close(self):
        gpib.EnableLocal(0, self.alist)

    def Send(self, str):
        gpib.Send(self.board, self.addr, str, len(str), 1)

#        def writeb( self, buff, len ) : # Added 010917/drb
#                gpib.writeb( self.id, buff )

    def Receive(self, len=512):
        result = ctypes.c_char_p('\000' * len)
        retval = gpib.Receive(self.board, self.addr, result, len, 0x0100)
        return result.value

    def clear(self):
        gpib.ibclr(self.id)

    def ibrsp(self):
        result = ctypes.c_char_p('\000' * 1)
        retval = gpib.ibrsp(self.id, result)
        return result.value


#        def wait(self,mask):
#                gpib.wait(self.id,mask)

#        def rsp(self):
#                self.spb = gpib.rsp(self.id)
#                return self.spb

#        def trigger(self):
#                gpib.trg(self.id)

#        def ren(self,val):
#                gpib.ren(self.id,val)
