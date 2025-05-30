from __future__ import print_function
from builtins import input
from builtins import object
import yaml
import importlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print(logger)
logger.info('INFO')


class nodev(object):
    def __init__(self, devname='switch'):
        self.devname = devname

    def enable(self):
        print('devname: %s, enable' % (self.devname))

    def disable(self):
        print('devname: %s, disable' % (self.devname))

    def set_lambda(self, att):
        print('devname: %s, set lambda: %f' % (self.devname, att))

    def set_att(self, att):
        print('devname: %s, set att: %f' % (self.devname, att))

    def set_latl(self, att):
        print('devname: %s, set latl: %f' % (self.devname, att))

    def set_range(self, rng):
        print('devname: %s, set range: %r' % (self.devname, rng))

    def set_navg(self, navg):
        print('devname: %s, set navg: %d' % (self.devname, navg))

    def set_volt(self, port, out):
        print('devname: %s, set v out: %d, %f' % (self.devname, port, out))

    def set_route(self, out):
        self.route(out)

    def route(self, *args):
        print('devname: %s, route %d' % (self.devname, args[0]))

    def get_route(self, *args):
        msgin = eval(input('%s, enter route' % self.devname))
        return int(msgin)

    def writeconfig(self, fp):
        fp.write('# no %s' % self.devname)

    def get_atime(self):
        msgin = eval(input('%s, enter atime/navg' % self.devname))
        return int(msgin)

    def get_atim(self):
        return self.get_atime()

    def get_range(self):
        msgin = eval(input('%s, enter range' % self.devname))
        if msgin == 'auto':
            return msgin
        else:
            return int(msgin)

    def get_lopt(self):
        msgin = eval(input('%s, enter enable/disable: ' % self.devname))
        return int(msgin)

    def get_volt(self):
        return float(eval(input('%s, enter dmm volt' % self.devname)))

    def get_power(self):
        return float(eval(input('%s, enter power' % self.devname)))

    def get_lambda(self):
        msgin = eval(input('%s, enter wavelength' % self.devname))
        return float(msgin)

    def get_att(self):
        msgin = eval(input('%s, enter att' % self.devname))
        return float(msgin)

    def get_latl(self):
        return self.get_att()


def make_instance(instr, module):
    if instr['intf'] == 'gpib':  # handle gpib device
        if 'gpib' in instr['port']:  # This is an NI device
            # raise NotImplementedError("NI interface needs to be coded")
            newaddr = 'dev%d' % instr['addr']
            #  implement later
            if 'device_number' in instr:
                return module.dev(newaddr, instr['slot'],
                                  instr['device_number'])
            elif 'slot' in instr:
                return module.dev(newaddr, instr['slot'])
            else:
                # return module.dev(newaddr, instr['port'])
                return module.dev(newaddr)
        else:  # Prologix device
            if 'device_number' in instr:
                # print(module.dev)
                return module.dev(instr['addr'], instr['port'], instr['slot'],
                                  instr['device_number'])
            elif 'slot' in instr:
                return module.dev(instr['addr'], instr['port'], instr['slot'])
            else:
                return module.dev(instr['addr'], instr['port'])
    if instr['intf'] == 'mccusb':
        path = None
        channel = 0
        if 'path' in instr:
            path = instr['path']
        if 'channel' in instr:
            channel = instr['channel']
        return module.dev(name=path, channel=channel)
    elif instr['intf'] == 'serial':
        return module.dev(instr['port'])
    else:
        raise NotImplementedError("non-gpib devices need to be implemented")


def load_yaml(yamlfile='config.yaml'):
    fp = open(yamlfile, 'r')
    instr_gen = yaml.load_all(fp)
    instr = {}
    for g in instr_gen:
        # print(g)
        instr[g['name']] = g
    fp.close()
    return instr


def create_instances_from_dict(instr, notFake=True):
    devModules = {}
    for key in list(instr.keys()):
        # print(key, instr[key])
        logger.info('loading: %r' % (instr[key]['inst']))
        instkey = instr[key]['inst']
        if notFake:
            if instkey not in devModules:
                devModules[instkey] = importlib.import_module(instkey)
            #  make an instance of the device
            instr[key]['dev'] = make_instance(instr[key], devModules[instkey])
        else:
            instr[key]['dev'] = nodev(key)
    # return instr


def create_instances(yamlfile='config.yaml', notFake=True):
    instr = load_yaml(yamlfile)
    create_instances_from_dict(instr, notFake=notFake)
    return instr


def create_instances_filter(yamlfile='config.yaml', notFake=True, match=None):
    instr = load_yaml(yamlfile)
    #  create a new dictionary of instruments of type match
    instr = {i: instr[i] for i in instr if instr[i]['type'] == match}

    devModules = {}
    for key in list(instr.keys()):
        # print(key, instr[key])
        logger.info('loading: %r' % (instr[key]['inst']))
        instkey = instr[key]['inst']
        if notFake:
            if instkey not in devModules:
                devModules[instkey] = importlib.import_module(instkey)
            #  make an instance of the device
            instr[key]['dev'] = make_instance(instr[key], devModules[instkey])
        else:
            instr[key]['dev'] = nodev(key)
    return instr
