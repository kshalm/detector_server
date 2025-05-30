from __future__ import print_function
import aq820133

params = [
    {
        'name': 'AQ820133 GPIB Address',
        'type': 'int',
        'limits': (1, 32),
        'value': 4
    },
    {
        'name': 'AQ820133 Slot',
        'type': 'int',
        'values': {1, 2, 3},
        'value': 3
    },
]


class dev(aq820133.dev):
    print('Change code to import aq820133 instead of aq8233')


if __name__ == '__main__':
    #att = dev(7,'COM8',1)
    att = dev(6, '/dev/ttyUSB0', 6)
    print(att.get_lambda())
    print(att.get_enable())
    """
    import sys
    #att.enable()
    #att.set_att(11)
    #print att.meter.query('ASHTR?')
    print repr(att.identify())
    att.writeconfig(sys.stdout)
    #att.disable()
    """
