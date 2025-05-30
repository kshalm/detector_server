"""
Wrapper python code for devSniffer.sh

Returns info on /dev/ devices
"""

import subprocess, pkg_resources

BASH_SCRIPT = pkg_resources.resource_filename('devSniffer', 'devSniffer.sh')

class devSniffer():
    def __init__(self):
        self.result = None
    def refresh_devices(self):
        raw_result = subprocess.check_output([BASH_SCRIPT])
        raw_result = raw_result.decode()
        parsed_result = [x.split("-") for x in raw_result.split("\n")]
        parsed_result.pop() #discard last item which is empty
        result = {}
        for item in parsed_result:
            result[item[0]] = item[1]
        self.result = result
    def list_all(self):
        self.refresh_devices()
        return self.result
    def find_by_dev(self, target):
        self.refresh_devices()
        search_results = []
        for serial, name in self.result.items():
            if serial.startswith(target):
                search_results.append((serial, name))
        return search_results
    def find_by_name(self, target):
        self.refresh_devices()
        search_results = []
        for serial, name in self.result.items():
            if name.startswith(target):
                search_results.append((serial, name))
        return search_results

if __name__ == "__main__":
    devSniffer = devSniffer()
    result = devSniffer.list_all()
    print(result)
