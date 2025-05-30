import yaml
import os
from usb_3100_wrapper import mccusb3100
from keithleyBiasControl import keithley
from zmqhelper.zmqbase import ZMQServiceBase
import json

def load_yaml(filename='det.yaml'):
    path = os.path.join(os.path.pardir, "config")
    filepath = os.path.join(path, filename)
    with open(filepath) as f:
        return yaml.safe_load(f)

def save_yaml_data(config_file, yaml_data):
    path = os.path.join(os.path.pardir, "config")
    filepath = os.path.join(path, config_file)
    with open(filepath, 'w') as f:
        yaml.dump(yaml_data, f)

# def connect_to_keithly(config_file):
#     yaml_data = load_yaml(config_file)
#     gpib = yaml_data['Keithley']['Info']['GpibAddr']
#     # try:
#     kc = keithley(gpib)
#     return kc, True
#     # except Exception:
#     #     return None, False

# def connect_to_mcc():
#     # try:
#     m = mccusb3100()
#     return m, True
#     # except Exception:
#     #     return None, False

# def reset_comparator(yaml_file):
#     if not DetectorControlService.mccPresent:
#         return False
#     cfg = load_yaml(yaml_file)
#     try:
#         ok = DetectorControlService.mcc.configV(cfg["Comparator"])
#         return bool(ok)
#     except Exception:
#         return False

# def reset_detectors(yaml_file):
#     if not DetectorControlService.biasControlPresent:
#         return False
#     cfg = load_yaml(yaml_file)
#     try:
#         ok = DetectorControlService.biasControl.resetConfig(cfg["Keithley"]["Bias"])
#         return bool(ok)
#     except Exception:
#         return False

def connect_to_keithly(configFile):
    yamlData = load_yaml(configFile)
    gpibaddr = yamlData['Keithley']['Info']['GpibAddr']
    try:
        biasControl = keithley(gpibaddr)
        biasControlPresent = True
    except:
        biasControl = None
        biasControlPresent = False
    return(biasControl, biasControlPresent)

def connect_to_mcc():
    try:
        mcc = mccusb3100()
        print(mcc.identify())
        mccPresent = True
    except:
        mcc = None
        mccPresent = False
    return(mcc, mccPresent)

# def load_yaml(filename = 'det.yaml'):
#     path = os.path.join(os.path.pardir, "config/")
#     # print(path)
#     filepath = os.path.join(path, filename)

#     with open(filepath) as f:
#         unorderedYamlData = yaml.safe_load(f)
#     return(unorderedYamlData)

# def save_yaml_data(configFile, yamlData):
#     path = os.path.join(os.path.pardir, "config/")
#     filepath = os.path.join(path, configFile)
#     print('filepath to write', filepath)
#     print(yamlData)
#     with open(filepath, 'w') as f:
#         yaml.dump(yamlData, f)


def set_comparator_channel(channelName, value, yamlFile = 'det.yaml'):
    """Sets comparator channels javascript style"""

    if mccPresent == False:
        return(False)
    yamlData = load_yaml(yamlFile)
    yamlData["Comparator"][channelName]['value'] = float(value)
    save_yaml_data(yamlFile, yamlData)

    success = reset_comparator(yamlFile)
    return(success)

def set_all_comparator_channels(comparatorSettings, yamlFile='det.yaml'):
    """Sets comparator channels javascript style"""

    if mccPresent == False:
        return(False)

    yamlData = load_yaml(yamlFile)

    for channelName, value in comparatorSettings.items():
        yamlData["Comparator"][channelName]['value'] = float(value)

    save_yaml_data(yamlFile, yamlData)
    success = reset_comparator(yamlFile)
    return(success)

def reset_comparator(yamlFile):
    if mccPresent == False:
        return(False)

    yamlData = load_yaml(yamlFile)
    success = True
    try:
        result = mcc.configV(yamlData["Comparator"])
        if result:
            print('Comparator (MCC) Channels set')
        else:
            print('Comparator (MCC) Error in setting voltages.')
            success = False
    except Exception as e:
        msg = "ERROR setting comparator channels %r" % e
        print(msg)
        success = False
    return(success)

def set_detector_channel(ch, voltage, yamlFile = 'det.yaml'):
    """Sets detector (Keithley213) channels """
    if biasControlPresent == False:
        return(False)
    yamlData = load_yaml(yamlFile)
    yamlData["Keithley"]["Bias"][ch] = float(voltage)
    save_yaml_data(yamlFile, yamlData)
    print(yamlData["Keithley"])
    success = reset_detectors(yamlFile)
    return(success)

def set_detector_voltage(ch, voltage, yamlFile = 'det.yaml'):
    success = biasControl.set_voltage(ch, voltage)
    if success:
        yamlData = load_yaml(yamlFile)
        yamlData["Keithley"]["Bias"][ch] = float(voltage)
        save_yaml_data(yamlFile, yamlData)
    return success

def set_all_detector_channels(biasSettings, yamlFile = 'det.yaml'):
    """Sets detector (Keithley213) channels """
    if biasControlPresent == False:
        return(False)

    yamlData = load_yaml(yamlFile)

    for ch, value in biasSettings.items():
        print(ch, value)
        yamlData["Keithley"]["Bias"][ch] = float(value)
    save_yaml_data(yamlFile, yamlData)

    success = reset_detectors(yamlFile)
    return(success)

def reset_detectors(yamlFile = 'det.yaml'):
    if biasControlPresent == False:
        return(False)

    yamlData = load_yaml(yamlFile)
    success = True

    try:
        result = biasControl.resetConfig(yamlData["Keithley"]["Bias"])

        if result:
            print("Keithley Channels Reset!")
        else:
            print("Keithley ERROR!")
            success = False
    except NameError as e:
        msg= "ERROR setting detector channels. Is Keithley plugged in? %r " % e
        print(msg)
        success = False
    except Exception as e:
        print("ERROR setting detector channels %r" % e)
        success = False
    return(success)


class DetectorControlService(ZMQServiceBase):
    def __init__(self, config_file='det.yaml', n_workers=1):
        
        self.config_file = config_file
        self.config = load_yaml(self.config_file)

        cParams = self.config['config_setup']
        if 'redis_host' not in cParams or cParams['register_redis'] is False:
            cParams['redis_host'] = None 
        if 'loki_host' not in cParams:
            cParams['loki_host'] = None
        if 'redis_port' not in cParams:
            cParams['redis_port'] = None
        if 'loki_port' not in cParams:
            cParams['loki_port'] = None
        
        super().__init__(rep_port = cParams['req_port'], 
            n_workers= n_workers,
            http_port = cParams['http_port'],
            loki_host = cParams['loki_host'],
            loki_port = cParams['loki_port'],
            redis_host = cParams['redis_host'],
            redis_port = cParams['redis_port'],
            service_name = cParams['service_name']
        )
        self.logger.info(f"Initializing {self.service_name} with config: {self.config}")
        print(f"Config file: {self.config}")
        
        # # establish hardware connections
        # # try:
        # self.biasControl, self.biasControlPresent = connect_to_keithly(self.config_file)
        # self.logger.info(f"Keithley Bias Control initialized: {self.biasControlPresent}")
        # print(f"Keithley Bias Control initialized: {self.biasControlPresent}")
        # # except Exception as e:
        #     # self.logger.error(f"Failed to connect to Keithley Bias Control: {e}")
        #     # os._exit(1)
        # # try:
        # self.mcc, self.mccPresent = connect_to_mcc()
        # self.logger.info(f"MCC USB-3100 initialized: {self.mccPresent}")
        # print(f"MCC USB-3100 initialized: {self.mccPresent}")
        # except Exception as e:
        #     self.logger.error(f"Failed to connect to MCC USB-3100: {e}")
        #     os._exit(1)
        
        self.logger.info(f"{self.service_name} initialized")

    def handle_request(self, message: str) -> str:
        self.logger.info(f"Received message: {message}")
        print(f"Received message: {message}")
        parts = message.split()
        cmd = parts[0].lower()

        # try:
            # if cmd == "test":
            #     return "Connected"

        if cmd == "commands":
            msg = json.dumps({
                "commands": [
                    "test",
                    "getconfig",
                    "resetdet",
                    "setdet",
                    "setdetconfig",
                    "setcomparatorconfig",
                    "setcomparatorchannel"
                ]
            })

        elif cmd == "getconfig":
            cfg = load_yaml(self.config_file)
            self.logger.info(f"Configuration loaded: {cfg}")
            msg = json.dumps(cfg)

        elif cmd == "resetdet":
            ok = reset_detectors(self.config_file)
            self.logger.info(f"Detectors reset: {ok}")
            msg = str(ok)

        elif cmd == "setdet":
            ch = int(parts[1])
            voltage = float(parts[2])
            ok = self.biasControl.set_voltage(ch, voltage) if self.biasControlPresent else False
            self.logger.info(f"Set Detector {ch} to {voltage}V: {ok}")
            msg = str(ok)

        elif cmd == "setvolt":
            ch = int(parts[1])
            voltage = float(parts[2])
            ok = self.biasControl.set_voltage(ch, voltage) if self.biasControlPresent else False
            self.logger.info(f"Set Voltage on channel {ch} to {voltage}V: {ok}")
            msg = str(ok)

        elif cmd == "setdetconfig":
            settings = json.loads(parts[1])
            cfg = load_yaml(self.config_file)
            for k, v in settings.items():
                cfg["Keithley"]["Bias"][int(k)] = float(v)
            save_yaml_data(self.config_file, cfg)
            ok = reset_detectors(self.config_file)
            self.logger.info(f"Detector configuration set: {ok}")
            msg = str(ok)

        elif cmd == "setcomparatorconfig":
            settings = json.loads(parts[1])
            cfg = load_yaml(self.config_file)
            for k, v in settings.items():
                cfg["Comparator"][k]['value'] = float(v)
            save_yaml_data(self.config_file, cfg)
            ok = reset_comparator(self.config_file)
            self.logger.info(f"Comparator configuration set: {ok}") 
            msg = str(ok)

        elif cmd == "setcomparatorchannel":
            channel = parts[1]
            value = float(parts[2])
            cfg = load_yaml(self.config_file)
            cfg["Comparator"][channel]['value'] = value
            save_yaml_data(self.config_file, cfg)
            ok = reset_comparator(self.config_file)
            self.logger.info(f"Set Comparator channel {channel} to {value}V: {ok}")
            msg = str(ok)
        else:
            self.logger.warning(f"Invalid command: {message}")
            msg = "Invalid Command"
        print(f"Response: {msg}")
        return msg

        # except Exception as e:
        #     self.logger.error(f"Error handling '{message}': {e}")
        #     return f"Error: {e}"

if __name__ == '__main__':
    configFile = 'det.yaml'  # Assuming the file is named 'det.yaml' in the config directory
    yamlData = load_yaml(configFile)
    print(yamlData)
    print('')
    biasControl, biasControlPresent = connect_to_keithly(configFile)
    mcc, mccPresent = connect_to_mcc()
    print(biasControl.identify())
    service = DetectorControlService(config_file='det.yaml', n_workers=1)
    service.start()   # blocks until SIGINT/SIGTERMworkers=1)