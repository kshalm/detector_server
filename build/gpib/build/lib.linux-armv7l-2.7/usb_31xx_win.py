from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import open
from builtins import int
from future import standard_library
standard_library.install_aliases()
from builtins import object
CBdotCFGpath = 'C:\\Users\\qittlab\\Documents\\python\\USB-31XX\\CB.CFG'
#CBdotCFGpath = 'C:\\ProgramData\\Measurement Computing\\DAQ\\CB.CFG'
# currently set to for test file, needs to be changed for real file
import inspect


def unimp():
    '''
  Tells the user the function they are tyring to use is not implimented in the version of the class they are using
  '''
    print('ERROR! Function ' + inspect.getouterframes(inspect.currentframe())[
        1][3] + ' is not implemented in this configuration')
    print('Included only for reference, returns -1')
    return -1


import sys
if sys.platform.startswith('win'):
    from ctypes import *
    boardNum = 0
    chan = 0
    gain = 100
    voltage = 2
    options = 0x0000

    def setVoltage(voltage, chan=0, boardNum=0, options=0x0000):
        if voltage > 10 or voltage < -10:
            raise ValueError("Voltage out of range")
        if voltage < 0:
            gain = 1
        else:
            gain = 100
        mcc = WinDLL('cbw64')
        cbVOut = mcc.cbVOut
        cbVOut.argtypes = [c_int, c_int, c_int, c_float, c_int]
        cbVOut(boardNum, chan, gain, voltage, options)


class usb31xx(object):
    def __init__(self):
        self.readCBdotCFG(CBdotCFGpath)

    def readCBdotCFG(self, path):
        self.CBdotCFG = open(path, 'r+')
        cfg = self.CBdotCFG
        lines = cfg.readlines
        self.config = {}
        cd = self.config

        def colonParse(line, cont):
            if type(cont) == dict:
                key, val = line.split(':')[:2]
                key = key.strip(' ')
                val = val.strip(' ')
                cont[key] = val
                return None
            elif type(cont) == list:
                index = int(line.split('[')[1].split(']')[0])
                while index > len(cont):
                    cont.append(None)
                cont.append(int(line.split(':')[1].strip(' ')))
                return cont

        for line in lines:
            if line.startswith('   Board #'):
                body = True
                self.config[line.strip(' ')] = {}
                cd = self.config[line.strip(' ')]
                continue
            if 'Misc Option[0]' in line:
                cd['Misc Options'] = []
                cd['Misc Options'] = colonParse(line, cd['Misc Options'])
                continue
            if 'Misc Option' in line:
                cd['Misc Options'] = colonParse(line, cd['Misc Options'])
                continue
            if not (body):
                colonParse(line, self.config)
            else:
                colonParse(line, cd)
            print('found Board #%s' % line.split('#')[1])

    def hex_codes(self):
        unimp()

    def USB31xx_blink(self, nBlinks):
        unimp()

    def USB31xx_Dout(self, value):
        unimp()

    def USB31xx_readMemoryFlash(self):
        unimp()

    def close(self):
        self.CBdotCFG.close()

    def msgScrub(self, msg):
        msg = msg.replace('[', '')
        msg = msg.replace(' ', '')
        msg = msg.replace(']', '')
        msg = msg.replace('\'', '')
        msg = msg.replace(',', ' ')
        return msg


'''
class usb31xx:
  def __init__(self, interval=1, average = 5, printOutput=False):
    self.hex_codes()
    self.printCommands = printOutput  #allow printing of messages
    self.printStatus = printOutput
    self.print_msgs('s',"Opening device")
    try:
        self.HIDid = hid.device(0x09db, 0x009c)     #open device for further commands
    except IOError, ex:
        try:
            self.HIDid = hid.device(0x9db, 0x9d)     #open device for further commands
        except IOError, ex:
            print ex
            print "You probably don't have the hard coded test hid. Update the hid.device line"
            print "in this script with one from the enumeration list output above and try again."
        
    self.print_msgs('s',"Manufacturer: %s" % self.HIDid.get_manufacturer_string()) #obtain device information
    self.print_msgs('s',"Product: %s" % self.HIDid.get_product_string())           #obtain device information
    self.print_msgs('s',"Serial No: %s" % self.HIDid.get_serial_number_string())   #obtain device information
    self.USB31xx_readMemoryFlash()     #get calibration fpor analouge outputs

  def hex_codes(self):
    
    
  def print_msgs(self,msgType,msg):
      if self.printCommands and msgType=='c':
          print msg
      if self.printStatus and msgType=='s':
          print msg
      
  def USB31xx_blink(self,nBlinks):
      self.print_msgs('c','blink %r times' %nBlinks)
      self.HIDid.write([self.hCode['BLINK'], nBlinks])
  
  def USB31xx_Dout(self, value):
      
  def USB31xx_Aout(self, port, aVolt):
      port = int(float(port))
      self.print_msgs('c','set voltage on port %r to %r V' %(port, aVolt))
      aVolt=int(aVolt/10.0*255*255)            #convert voltage to range
      aVolt = int(self.slope[port]*aVolt + self.offset[port])  #apply calibration
      highBit,lowBit = divmod(aVolt,255)     #split into 2 bits
      self.HIDid.write([self.hCode['AOUT_CONFIG'], port, 0]) #configure port for output
      self.HIDid.write([self.hCode['AOUT'], port, lowBit, highBit, 0])   #set voltage
  
  def USB31xx_Aout_all(self, aVolt=0.0):
      for port in range(0,8):
          self.USB31xx_Aout(port, aVolt)
  
  def msgScrub(self,msg):
      msg = msg.replace('[','')
      msg = msg.replace(' ','')
      msg = msg.replace(']','')
      msg = msg.replace('\'','')
      msg = msg.replace(',',' ')
      return msg
  
  def USB31xx_readMemoryFlash(self):
      ### reads and returns the slope and offset calibration data 
      ### for the USB3103/USB3104  analouge outputs
      self.print_msgs('s','loading analoge data from device')
      l=[]    #initialise empty aray
      stAddress = 0x100                           #start location of calibration data
      for x in range(0,8):                        #for each analouge output
          adr = stAddress+x*0x10                  #address to read from
          highBit,lowBit = divmod(int(adr),255)   # device can only read small bits at a time, so divide into 2 bits
          # infom device that you want to read from memory, at a certain address, and so many bytes
          self.HIDid.write([self.hCode['MEM_READ'] , lowBit, highBit, 0x0, 16])  
          time.sleep(0.1)         #wait 0.1 seconds
          msg=self.msgScrub(str(self.HIDid.read(16))) # read from memort and turn to string, remove characters from msg, replace(,) with space
          for y in msg.split():   # split message into chuncks, then for each chunk
              try:                # attept to
                  l.append(y)     # append chunk into an array
              except ValueError:  # if append operation fails
                  pass            # do  nothing 
              
      self.slope=[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]     #initialise slope array
      self.offset=[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]    #initialise ofset array
      for x in range (0,8):       # Once for each output
          adr = x*16              # there are 16 bytes of information for each output
          for y in range(0,5,4):  # y = 0,4. 0 for the adress of slopes, 4 for the addess of offsets
              floatPack=''            # create empty string
              for z in range(0,4):    # read through 4 consecutive adresses
                  a=bytes(chr(int(l[adr+y+z]))) #turn string > integer > character > byte
                  floatPack=floatPack+a       #add byte to byte string
              #unpack a 4 byte string into a tupple, convert to string then remove characters         
              floatStr=str(struct.unpack('f',floatPack)).strip(',()')
              if y==0:            #add float to slope configuratiom
                  self.slope[x]= float(floatStr)
              elif y==4:          #add float to offset configuratiom
                  self.offset[x]= float(floatStr)    
      self.print_msgs('s','loaded slopes and offsets')
      
  def close(self):
      self.print_msgs('s',"Closing device")
      self.HIDid.close()
'''
