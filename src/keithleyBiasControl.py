"""
Controlling Keithley213 via gpib3 library

Some modifications by Collin Schlager
"""

import Keithley213
import time
import os
from serial.tools import list_ports

#Use devSniffer to find serial port!

def find_com(string):
    print('in find_com')
    for port in list_ports.comports():
        # print('checking port', port)
        if string.lower() in port[1].lower():
            print("Found device :" , port[1].lower())
            return port[0]
    raise Exception(
        "Failed to find device : {}, reverting to config file".format(string))
    return 0

class keithley():
    def __init__(self, gpibaddr = 10):
        searchString = 'Prologix'
        self.serialport = find_com(searchString)
        print(self.serialport)
        if self.serialport == 0:
            print('Keithley 213 device not found')
            self.vsrc = None
        else:
            self.gpibaddr = gpibaddr
            self.vsrc = Keithley213.dev(self.gpibaddr, self.serialport)
            print(self.vsrc.identify())

    def set_voltage(self,channel, voltage):
        self.vsrc.set_volt(channel, voltage)
        return True
        
    def reset(self, channel, voltage):
        self.vsrc.set_volt( channel, 0.0)
        time.sleep(2)
        self.vsrc.set_volt(channel, voltage)
        print("Set channel %r to %r" % (channel, voltage))
        #print(get_volt(channel))
        return True

    def identify(self):
        return self.vsrc.identify()

    def get_volt(self, channel):
        return self.vsrc.get_volt(channel,12)

    def resetConfig(self, configFile, waitTime = 2.):
        """Added by Collin Schlager (summer 2017)
        Given a dictionary (like a yaml config file), set the voltages accordingly"""
        for channel in configFile:
            channel = int(channel)
            print("Channel %r to 0V" % channel)
            self.vsrc.set_volt(channel, 0.)
        # print("Wait 2 sec...")
        time.sleep(waitTime)
        for channel, voltage in configFile.items():
            channel = int(channel)
            voltage = float(voltage)
            print("Channel %r to %rV" % (channel, voltage))
            self.vsrc.set_volt(channel, voltage)
        print("Complete")
        return True

    def identify(self):
        return(self.vsrc.identify())

if __name__ == '__main__':
    # print("Loaded.")
    #testNewVoltages = {'1':'0.44','2':'0.01'}
    #originalVoltages = {'1':'0.45','1':'0.0'}
    #print(testNewVoltages)
    #resetConfig(testNewVoltages)
    # reset(2, 0.)
    vsrc = keithley(10)
