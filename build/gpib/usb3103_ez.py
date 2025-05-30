from builtins import input
import usb31xx
import sys

ch = 6
if sys.argv > 1:
    ch = int(sys.argv[1])

vsource = usb31xx.usb31xx()

while True:
    strin = input('%d voltage: ' % ch)
    vsource.USB31xx_Aout(ch, float(strin))
