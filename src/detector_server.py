import yaml
import os
from usb_3100_wrapper import mccusb3100
from keithleyBiasControl import keithley
from zmqhelper.zmqbase import ZMQServiceBase

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

def connect_to_keithly(config_file):
    yaml_data = load_yaml(config_file)
    gpib = yaml_data['Keithley']['Info']['GpibAddr']
    try:
        kc = keithley(gpib)
        return kc, True
    except Exception:
        return None, False

def connect_to_mcc():
    try:
        m = mccusb3100()
        return m, True
    except Exception:
        return None, False

def reset_comparator(yaml_file):
    if not DetectorControlService.mccPresent:
        return False
    cfg = load_yaml(yaml_file)
    try:
        ok = DetectorControlService.mcc.configV(cfg["Comparator"])
        return bool(ok)
    except Exception:
        return False

def reset_detectors(yaml_file):
    if not DetectorControlService.biasControlPresent:
        return False
    cfg = load_yaml(yaml_file)
    try:
        ok = DetectorControlService.biasControl.resetConfig(cfg["Keithley"]["Bias"])
        return bool(ok)
    except Exception:
        return False

class DetectorControlService(ZMQServiceBase):
    def __init__(self, config_file='det.yaml', n_workers=1):
        
        self.config_file = config_file
        self.config = self.load_yaml(self.config_file)
        
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
        
        
        # establish hardware connections
        try:
            self.biasControl, self.biasControlPresent = connect_to_keithly(self.config_file)
            self.logger.info(f"Keithley Bias Control initialized: {self.biasControlPresent}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Keithley Bias Control: {e}")
            os._exit(1)
        try:
            self.mcc, self.mccPresent = connect_to_mcc()
            self.logger.info(f"MCC USB-3100 initialized: {self.mccPresent}")
        except Exception as e:
            self.logger.error(f"Failed to connect to MCC USB-3100: {e}")
            os._exit(1)
        
        self.logger.info(f"{self.service_name} initialized")

    def handle_request(self, message: str) -> str:
        self.logger.info(f"Received message: {message}")
        parts = message.split()
        cmd = parts[0].lower()

        try:
            # if cmd == "test":
            #     return "Connected"

            if cmd == "commands":
                return json.dumps({
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

            if cmd == "getconfig":
                cfg = load_yaml(self.config_file)
                self.logger.info(f"Configuration loaded: {cfg}")
                return json.dumps(cfg)

            if cmd == "resetdet":
                ok = reset_detectors(self.config_file)
                self.logger.info(f"Detectors reset: {ok}")
                return str(ok)

            if cmd == "setdet":
                ch = int(parts[1])
                voltage = float(parts[2])
                ok = self.biasControl.set_voltage(ch, voltage) if self.biasControlPresent else False
                self.logger.info(f"Set Detector {ch} to {voltage}V: {ok}")
                return str(ok)

            if cmd == "setvolt":
                ch = int(parts[1])
                voltage = float(parts[2])
                ok = self.biasControl.set_voltage(ch, voltage) if self.biasControlPresent else False
                self.logger.info(f"Set Voltage on channel {ch} to {voltage}V: {ok}")
                return str(ok)

            if cmd == "setdetconfig":
                settings = json.loads(parts[1])
                cfg = load_yaml(self.config_file)
                for k, v in settings.items():
                    cfg["Keithley"]["Bias"][int(k)] = float(v)
                save_yaml_data(self.config_file, cfg)
                ok = reset_detectors(self.config_file)
                self.logger.info(f"Detector configuration set: {ok}")
                return str(ok)

            if cmd == "setcomparatorconfig":
                settings = json.loads(parts[1])
                cfg = load_yaml(self.config_file)
                for k, v in settings.items():
                    cfg["Comparator"][k]['value'] = float(v)
                save_yaml_data(self.config_file, cfg)
                ok = reset_comparator(self.config_file)
                self.logger.info(f"Comparator configuration set: {ok}") 
                return str(ok)

            if cmd == "setcomparatorchannel":
                channel = parts[1]
                value = float(parts[2])
                cfg = load_yaml(self.config_file)
                cfg["Comparator"][channel]['value'] = value
                save_yaml_data(self.config_file, cfg)
                ok = reset_comparator(self.config_file)
                self.logger.info(f"Set Comparator channel {channel} to {value}V: {ok}")
                return str(ok)
            self.logger.warning(f"Invalid command: {message}")
            return "Invalid Command"

        except Exception as e:
            self.logger.error(f"Error handling '{message}': {e}")
            return f"Error: {e}"

if __name__ == '__main__':
    service = DetectorControlService(config_file='det.yaml', n_workers=1)
    service.start()   # blocks until SIGINT/SIGTERMworkers=1)
    service.start()   # blocks until SIGINT/SIGTERM