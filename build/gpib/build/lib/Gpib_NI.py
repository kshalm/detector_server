from __future__ import print_function
from builtins import object
import os, sys, ctypes, time
#from ctypes import *
import threading
import logging

logger = logging.getLogger(__name__)
# logger.addHandler(logging.NullHandler())
gpiblock = threading.Lock()

NI4882 = False
GPIB32 = False
try:
    print('trying to load National Instruments driver: ni4482')
    gpib = getattr(ctypes.windll, "ni4882")
    NI4882 = True
    print('loaded ni4882')
except:
    print('failed to load ni4882')

if NI4882 == False:
    print('trying to load National Instruments driver: gpib-32')
    gpib = getattr(ctypes.windll, "gpib-32")
    print('loaded gpib-32')

RQS = (1 << 11)
SRQ = (1 << 12)
TIMO = (1 << 14)


class Gpib(object):
    def __init__(self, name='gpib0'):
        #self.id = gpib.ibfindA(name)
        #self.error = gpib.error
        board = 0
        pad = int(name.lstrip('dev'))
        sad = 0
        timeout = 10  # 1sec
        eot = 1
        eos = 0
        self.id = gpib.ibdev(board, pad, sad, timeout, eot, eos)
        self.lock = gpiblock

    def close(self):
        gpib.ibonl(self.id, 0)

    def query(self, msg, wait=0.2, attempts=5):
        self.write(msg)
        time.sleep(wait)
        msgin = self.readline()
        return msgin

    def query_old(self, msg, wait=0.2, attempts=5):
        self.write(msg)
        time.sleep(wait)
        msgin = self.read()
        counter = 0
        while len(msgin) == 0:
            if counter > attempts:
                break
            msgin = self.read()
            counter += 1
        return msgin

    def write(self, str):
        gpib.ibwrt(self.id, str, len(str))

#        def writeb( self, buff, len ) : # Added 010917/drb
#                gpib.writeb( self.id, buff )

    def read(self, length=512):
        # result = ctypes.c_char_p('\000' * int(length))
        result = ctypes.create_string_buffer(length)
        # print('ibcnt', gpib.Ibcnt())
        retval = gpib.ibrd(self.id, result, int(length))
        return result.value

    def readline(self):
        msg = ''
        loop = True
        read_timeout = 1
        start = time.time()
        while loop:
            m = self.read(100)
            if len(m) > 0:
                msg += m
            else:
                time.sleep(0.1)
            if '\n' in msg:
                break
            if (time.time() - start) > read_timeout:
                logger.info('exceed timeout readline' + repr(msg))
                break
        # print('readline',repr(msg))
        return msg  #  Might need to split at \n if there is a problem

    def readbinary(self, count=512):
        result = ctypes.create_string_buffer(count)
        retval = gpib.ibrd(self.id, result, count)
        return result.raw

    def readb(self, len=512):
        result = ctypes.c_char_p('\000' * len)
        retval = gpib.ibrd(self.id, result, len)
        print(retval)
        print(len(result))
        return result

    def clear(self):
        gpib.ibclr(self.id)

    def tmo(self, value=11):
        gpib.ibtmo(self.id, value)

    def eos(self, value=0xA):
        gpib.ibeos(self.id, 0x1400 + value)

    def config(self, param1, param2):
        #print 'config %d %d'%(param1,param2)
        gpib.ibconfig(self.id, param1, param2)

#        def wait(self,mask):
#                gpib.wait(self.id,mask)

    def rsp(self):
        # result = ctypes.c_char_p('\000')
        result = ctypes.create_string_buffer(1)
        #res = ctypes.c_char('0')
        #self.spb = gpib.ibrsp(self.id,ctypes.byref(res))
        self.spb = gpib.ibrsp(self.id, result)
        if self.spb & (1 << 8):
            # if len(result.value) > 0:
            return ord(result.raw)
        else:
            return -256
            #return ord(result.value)

        #        def trigger(self):
        #                gpib.trg(self.id)
    def loc(self):
        gpib.ibloc(self.id)

    def close(self):
        self.loc()


#        def ren(self,val):
#                gpib.ren(self.id,val)
