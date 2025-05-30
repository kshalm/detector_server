# -*- coding: utf-8 -*-
"""
Gpib controller for
Keithley 2400 Source Meter
Created on Tue Jun 27 14:45:37 2017
@author: zsteffen
"""

import Gpib
import time

class dev:
    def __init__(self,addr,serialport):
        #self.meter, self.addr, self.port
        self.meter = Gpib.Gpib(addr,serialport)
        #meter = self.meter
        iden = self.meter.query('*IDN?\n')
        print(iden)
    
    def get_I(self):
        self.meter.write(':sour:volt:mode fixed\n')
        self.meter.write(':sour:curr:mode fixed\n')
        self.meter.write(':meas:curr?\n')
        time.sleep(.1)
        val = self.meter.readline()
        sval = val.decode().split(',')
        return float(sval[1])

    def get_V(self):
        self.meter.write(':sour:volt:mode fixed\n')
        self.meter.write(':sour:curr:mode fixed\n')
        self.meter.write(':meas:volt?\n')
        time.sleep(.1)
        val = self.meter.read()
        sval = val.decode().split(',')
        return float(sval[0])
        
    def get_R(self):
        self.meter.write(':meas:res?\n')
        time.sleep(.1)
        val = self.meter.read()
        sval = val.decode().split(',')
        return float(sval[2])
    
    def output_off(self):
        self.meter.write(':outp:stat 0\n')
        
    def output_on(self):
        self.meter.write(':outp:stat 1\n')
        
    def set_I(self,amps=0.0):
        self.meter.write(':sour:func CURR\n')
        self.meter.write(':sour:curr %f\n' %amps)
        
    def set_V(self,volts=0.0):
        self.meter.write(':sour:func VOLT\n')
        self.meter.write(':sour:volt %f\n' %volts)
        
    def sweep_V(self,v_start,v_stop,v_step,delay = 1,prot_curr = 1e-6): #uses the scopes built in sweep function
        self.meter.write('*rst\n')
        #self.meter.write(':sour:func:mode volt\n')
        #self.meter.write(':sens:func:all\n')
        #self.meter.write(':sens:func:off "res"\n')
        self.meter.write(':sour:func volt\n')
        self.meter.write(':sens:curr:prot %f\n' %prot_curr)
        self.meter.write(':sens:volt:nplc %f\n' %delay)  #delay = wall power cycles between measurments
        self.meter.write(':sens:curr:nplc %f\n' %delay) #min delay .01 max 10
        self.meter.write(':sour:volt:star %s\n' %v_start)
        self.meter.write(':sour:volt:stop %s\n' %v_stop)
        self.meter.write(':sour:volt:step %s\n' %v_step) #minimum voltage step is 5uV, 
             #smaller v_step will give multiple measurements at each 5uV increment
        self.meter.write(':sour:volt:mode swe\n')
        self.meter.write(':sour:swe:rang auto\n')
        self.meter.write(':sour:swe:spac lin\n')
        steps = (v_stop-v_start)/v_step
        self.meter.write(':trig:coun %d\n' %steps)
        self.output_on()
        time.sleep(.5)
        self.meter.write(':read?')
        """
        #the buffer that 'read' gives us is long. read it all out with what follows
        data = ''.encode() 
        loop = True
        nstr = '\n'.encode()
        
        while loop:
            #time.sleep(.05) #careful, when the source meter is in talk mode and you call read it gets stuck
            m = self.meter.read(1000) 
            #print(m[0:5])
            if len(m)>0:
                data += m
            else:
                time.sleep(0.1)
                print('slept')
            if nstr in data:
                break;
        """
        time.sleep(delay)
        data = self.meter.readline() #not sure if this will work with python2
        #self.output_off()
        #self.meter.close()
        return data
    
    def sweep_I(self,i_start,i_stop,i_step,delay = 1):
        self.meter.write('*rst\n')
        self.meter.write(':sour:func curr \n')
        self.meter.write(':sens:func "volt"\n')
        self.meter.write(':sens:func "curr"\n')
        self.meter.write(':sens:volt:nplc %f\n' %delay)
        self.meter.write(':sens:curr:nplc %f\n' %delay)
        self.meter.write(':sour:curr:star %s\n' %i_start)
        self.meter.write(':sour:curr:stop %s\n' %i_stop)
        self.meter.write(':sour:curr:step %s\n' %i_step)
        self.meter.write(':sour:curr:mode swe\n')
        self.meter.write(':sour:swe:rang auto\n')
        self.meter.write(':sour:swe:spac lin\n')
        steps = (i_stop-i_start)/i_step
        self.meter.write(':trig:coun %d\n' %steps)
        self.output_on()
        time.sleep(.25)
        self.meter.write(':read?')
        data = ''
        loop = True
        while loop:
            m = self.meter.read(100)
            if len(m)>0:
                data += m
            else:
                time.sleep(0.1)
            if '\n' in data:
                break;
                
        self.output_off()
        self.meter.close()
        return data
        
        
        
        
        
        
        
        