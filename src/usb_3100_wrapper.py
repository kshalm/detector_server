import usb_3100
import time

class mccusb3100:
    def __init__(self):
        self.dev = self.initialize()
        # print(self.dev)

    def initialize(self):
        try:
          mcc = usb_3100.usb_3101()
        except:
          try:
            mcc = usb_3100.usb_3102()
          except:
            try:
              mcc = usb_3100.usb_3103()
            except:
              try:
                mcc = usb_3100.usb_3104()
              except:
                try:
                  mcc = usb_3100.usb_3105()
                except:
                  try:
                    mcc = usb_3100.usb_3106()
                  except:
                    try:
                      mcc = usb_3100.usb_3110()
                    except:
                      try:
                        mcc = usb_3100.usb_3112()
                      except:
                        try:
                          mcc = usb_3100.usb_3114()
                        except:
                          print('No USB-31XX device found')
                          mcc = None
        return(mcc)

    def reset(self):
        self.dev.Reset()
        # self.close()

    def blink(self, n):
        self.dev.Blink(n)

    def setV(self, voltage, channel=1):
        gain = 0
        channel = int(channel)
        value = self.dev.volts(gain, voltage)
        self.dev.AOutConfig(channel, gain)
        self.dev.AOut(channel, value, 0)
        return(voltage)

    def configV(self, configFile):
        for item in configFile:
            channel = configFile[item]['ch']
            voltage = configFile[item]['value']
            self.setV(voltage, channel)
        return(True)

    def getV(self, channel):
        return('')

    def identify(self):
        info = {}
        info["Manufacturer"] =  self.dev.h.get_manufacturer_string()
        info["Product"] = self.dev.h.get_product_string()
        info["Serial No"] = self.dev.h.get_serial_number_string()
        return(info)

    def close(self):
        self.dev.h.close()
        # self.dev.h.exit()
        return()

if __name__ == "__main__":
  mcc = mccusb3100()
  print(mcc.identify())
  # mcc.setV(0,1)
  # mcc.reset()

  # time.sleep(1)
  # # usb_3100 = reload(usb_3100)
  # deep_reload(usb_3100)
  # mcc = None
  # mcc = mccusb3100()
  # print(mcc.identify())
  # # print('set voltage sucessfully')
