import yaml
import os
from usb_3100_wrapper import mccusb3100
from keithleyBiasControl import keithley
import json
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
    def __init__(self, config_file='det.yaml'):
        super().__init__(
            rep_port=56000,
            http_port=8080,
            service_name='detector_control',
            n_workers=1
        )
        self.config_file = config_file
        # establish hardware connections
        self.biasControl, self.biasControlPresent = connect_to_keithly(self.config_file)
        self.mcc, self.mccPresent = connect_to_mcc()
        self.logger.info("DetectorControlService initialized")

    def handle_request(self, message: str) -> str:
        parts = message.split()
        cmd = parts[0].lower()

        try:
            if cmd == "test":
                return "Connected"

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
                return json.dumps(cfg)

            if cmd == "resetdet":
                ok = reset_detectors(self.config_file)
                return str(ok)

            if cmd == "setdet":
                ch = int(parts[1])
                voltage = float(parts[2])
                ok = self.biasControl.set_voltage(ch, voltage) if self.biasControlPresent else False
                return str(ok)

            if cmd == "setvolt":
                ch = int(parts[1])
                voltage = float(parts[2])
                ok = self.biasControl.set_voltage(ch, voltage) if self.biasControlPresent else False
                return str(ok)

            if cmd == "setdetconfig":
                settings = json.loads(parts[1])
                cfg = load_yaml(self.config_file)
                for k, v in settings.items():
                    cfg["Keithley"]["Bias"][int(k)] = float(v)
                save_yaml_data(self.config_file, cfg)
                ok = reset_detectors(self.config_file)
                return str(ok)

            if cmd == "setcomparatorconfig":
                settings = json.loads(parts[1])
                cfg = load_yaml(self.config_file)
                for k, v in settings.items():
                    cfg["Comparator"][k]['value'] = float(v)
                save_yaml_data(self.config_file, cfg)
                ok = reset_comparator(self.config_file)
                return str(ok)

            if cmd == "setcomparatorchannel":
                channel = parts[1]
                value = float(parts[2])
                cfg = load_yaml(self.config_file)
                cfg["Comparator"][channel]['value'] = value
                save_yaml_data(self.config_file, cfg)
                ok = reset_comparator(self.config_file)
                return str(ok)

            return "Invalid Command"

        except Exception as e:
            self.logger.error(f"Error handling '{message}': {e}")
            return f"Error: {e}"

if __name__ == "__main__":
    service = DetectorControlService()
    service.start()   # blocks until SIGINT/SIGTERM
