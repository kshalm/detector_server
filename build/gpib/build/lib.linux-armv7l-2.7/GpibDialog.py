from __future__ import print_function
from PyQt4.QtGui import QDialog, QVBoxLayout, QDialogButtonBox, QDateTimeEdit, QApplication
from PyQt4.QtCore import Qt, QDateTime
from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
from copy import deepcopy
#GUI
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import serial.tools.list_ports
import usb_intf


def smart_merge_params(p1, p2):
    for item_in2 in p2:
        found_in1 = False
        for item_in1 in p1:
            if item_in2['name'] == item_in1['name']:
                found_in1 = True
                break
        if not found_in1:
            p1.append(item_in2)


def config_any(parent, groupparam, keyname2, instparams, module_dict, **kw):
    #global tab2
    #groupparam = tab2.p
    #keyname = 'meter'
    #keyname2 = 'Voltage Meter'
    inst = groupparam[keyname2]
    usedefault = groupparam.param(keyname2).valueIsDefault()
    #print 'config_any, inst:',inst
    #print usedefault
    #print 'instparams',instparams
    if keyname2 in instparams and (usedefault):
        print('using previously loaded params for %s' % (keyname2))
        params = instparams[keyname2]
        #print params
        if inst in module_dict:  # not sure why we are checking here but duplicating below
            if hasattr(module_dict[inst], 'params'):
                p = module_dict[inst].params
                for item in p:
                    found = False
                    for item2 in params:
                        if item['name'] == item2['name']:
                            found = True
                            break
                    if not found:
                        print('Missing %s' % item['name'])
                        print('Adding to parameter list')
                        params.append(item)
    else:
        params = [
            {
                'name': 'GPIB interface type',
                'type': 'list',
                'values': {
                    "NI": 1,
                    "Prologix": 2,
                    'Fake': 3,
                    'Serial': 4,
                    'USBTMC': 5
                },
                'value': 1
            },
            {
                'name': 'GPIB interface name',
                'type': 'list',
                'values': {
                    'gpib0': 'gpib0'
                },
                'value': 'gpib0'
            },
        ]
        if inst in module_dict:
            print('creating new parameter list, found module dict key for %s' %
                  inst)
            if hasattr(module_dict[inst], 'params'):
                params.extend(module_dict[inst].params)
            else:
                print('no params in module, adding gpib address')
                params.append({
                    'name': 'GPIB address',
                    'type': 'int',
                    'value': 1,
                    'limits': (1, 32),
                    'extra': 'extra'
                })
                print(params)
    if 'extra_params' in kw:
        smart_merge_params(params, kw['extra_params'])
    params = GpibParameter(name=keyname2, children=params)
    s, p, r = ConfigDialog.getconfig(params, parent)
    if r == QtGui.QDialog.Accepted:
        groupparam.param(keyname2).setDefault(inst)
    instparams[keyname2] = s
    #inst_params[keyname]=p
    #print p['GPIB interface name'],p['GPIB interface type']
    #print instparams[keyname]


class GpibParameter(pTypes.GroupParameter):
    def __init__(self, **opts):
        self.mynamedict = {'gpib0': 'gpib0'}
        opts['type'] = 'group'
        pTypes.GroupParameter.__init__(self, **opts)
        #self.addChild({'name':'GPIB interface type','type':'list','values':{"NI":1, "Prologix":2, "fake":3},'value':1})
        #self.addChild({'name':'GPIB interface name','type':'list','values':self.mynamedict, 'value':'gpib0'})
        #print self.childs
        #print self.type()
        self.gpibtype = self.param('GPIB interface type')
        self.gpibtype.sigValueChanged.connect(self.TypeChanged)
        #print 'children',self.children()
    def OptsChanged(self):
        print("OptsChanged")
        #print self.gpibname.opts
        #self.addChild(self.gpibname)
        #self.updateDisplayLabel()
    def TypeChanged(self):
        typevalue = self.gpibtype.value()
        # find 'GPIB interface name' parameter and remove
        #print 'TypeChanged'
        #print 'self.childs',self.childs
        #print 'self.children()',self.children()
        for item in self.childs:
            if 'interface name' in item.name():
                print('found item:', item)
                self.removeChild(item)
        #self.removeChild(self.childs[1])
        #print 'Type now: ', typevalue 
        for item in self.childs:
            if 'ddress' in item.name():
                item.show()
        if typevalue == 1:  # NI
            self.mynamedict = {'gpib0': 'gpib0'}
        elif typevalue == 2:  # Prologix
            self.mynamedict = {}
            ports = serial.tools.list_ports.comports()
            for port in ports:
                self.mynamedict[port[0]] = port[0]
        elif typevalue == 3:  # fake
            self.mynamedict = {'fake': 'fake'}
        elif typevalue == 4:  # serial
            self.mynamedict = {}
            ports = serial.tools.list_ports.comports()
            for port in ports:
                self.mynamedict[port[0]] = port[0]
            for item in self.childs:
                if 'ddress' in item.name():
                    item.hide()
        elif typevalue == 5:  # usbtmc
            self.mynamedict = {}
            ports = usb_intf.list_ports()
            for port in ports:
                self.mynamedict[port] = port
            for item in self.childs:
                if 'ddress' in item.name():
                    item.hide()
        else:
            self.mynamedict = {'fake': 'fake'}
        #print self.mynamedict
        self.insertChild(1, {
            'name': 'GPIB interface name',
            'type': 'list',
            'values': self.mynamedict
        })
        #print self.gpibname.opts
    def addChilds(self, paramlist):
        for param in paramlist:
            self.addChild(param)


class ConfigDialog(QtGui.QDialog):
    def __init__(self, params, parent=None):
        super(ConfigDialog, self).__init__(parent)
        self.setModal(True)  # make the program wait for input
        #print 'config dialog initial type(params) ',type(params)
        self.params = params
        self.setWindowTitle('Gpib Setting')
        if isinstance(params, list):  # create parameter from a list
            p = Parameter.create(
                name='GpibSettings', type='group', children=params)
        else:
            p = params  # If parameter is already a parameter, create a list that could generate 'p'
            # create a list of he parameters in case things are canceled
            state = []
            for kid in p.children():
                #print kid.name(), kid.value(), kid.children(), kid.type()
                state.append(deepcopy(kid.opts))
            self.params = state
        t = ParameterTree(parent=None)
        t.setParameters(p, showTop=False)

        layout = QtGui.QGridLayout()
        self.setLayout(layout)
        #layout.addWidget(QtGui.QLabel("User Inputs"),0,0,1,1)
        #layout.addWidget(t,1,0,1,1)

        layout.addWidget(t, 0, 0, 1, 1)
        self.resize(400, 400)
        self.p = p

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        layout.addWidget(self.buttons, 1, 0, 1, 1)

        self.installEventFilter(self)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.show()  # only this line ad next line needed on OS X
        self.raise_()  # this must be after show to put it on top
        #self.activateWindow()
    def eventFilter(self, source, event):
        #if (event.type() != 12) and (event.type()!=77):
        #    print source, ' event filter ',event.type()
        #    print source is self
        if (event.type() == QtCore.QEvent.KeyPress) or (event.type() == 51):
            #print 'key: ',event.key()
            if event.key() == QtCore.Qt.Key_Return:
                self.accept()
                return True
        #return QtGui.QWidget.eventFilter(self, source, event)
        return QtGui.QDialog.eventFilter(self, source, event)

    def accept(self):
        super(ConfigDialog, self).accept()
        #print 'accept'
        # create new params list that has changes to the setup
        state = []
        for kid in self.p.children():
            #print kid.name(), kid.value(), kid.children(), kid.type()
            state.append(kid.opts)  # not sure if I need to do a deepcopy here
            # reassign all values whether changed or not
            '''
            for item in params:
                if item['name']==kid.name():
                    item['value'] = kid.value()
            '''
        self.params = state

    def reject(self):
        super(ConfigDialog, self).reject()
        #print 'cancel'
        #print self.params
    def keyPressEvent(self, event):
        #print event
        #print event.key()
        if event.key() == QtCore.Qt.Key_Escape:
            self.reject()
        elif event.key() == QtCore.Qt.Key_Return:
            print('keypress return')
            self.accept()
            #super(ConfigDialog,self).keyPressEvent(event)
        else:
            super(ConfigDialog, self).keyPressEvent(event)

    def getparams(self):
        return self.params

    @staticmethod
    def getconfig(params, parent=None):
        dialog = ConfigDialog(params, parent)
        result = dialog.exec_()
        return dialog.params, dialog.p, result


if __name__ == '__main__':
    app = QApplication([])
    #  d = TestDialog() 
    """
  params = [
    {'name':'address','type':'str','value':'Type something here'},
    {'name':'Notes','type':'str','value':'Type something here'},
    {'name':'Number', 'type':'int','value':3},
  ]
  """
    params = [
        {
            'name': 'GPIB interface type',
            'type': 'list',
            'values': {
                "NI": 1,
                "Prologix": 2,
                'Fake': 3,
                'Serial': 4,
                'USBTMC': 5
            },
            'value': 1
        },
        {
            'name': 'GPIB interface name',
            'type': 'list',
            'values': {
                'gpib0': 'gpib0'
            },
            'value': 'gpib0'
        },
        {
            'name': 'address',
            'type': 'int',
            'value': 4
        },
    ]
    params = GpibParameter(name='gpib interface', children=params)
    #params['GPIB interface type']=2
    #params['GPIB interface name']='/dev/cu.Bluetooth-Modem'
    #params.addChild( {'name':'address','type':'int','value':4})
    params.addChilds(({
        'name': 'address1',
        'type': 'int',
        'value': 5
    }, {
        'name': 'address2',
        'type': 'int',
        'value': 6
    }))

    params['address'] = 5
    #print params.param('address2').name()
    print(params.getValues())
    """
  d = ConfigDialog(params)
  d.show()
  d.raise_()
  """
    s, p, r = ConfigDialog.getconfig(params)
    #print s 
    params = GpibParameter(name='gpib interface', children=s)
    s, p, r = ConfigDialog.getconfig(params)

    print(p['address'], p['GPIB interface name'], p['GPIB interface type'])
    #app.exec_()
"""
    def keyPressEvent(self, event):
            if event.key() == QtCore.Qt.Key_Escape:
                    if self.hidden==True:
                        self.show()
                        self.hidden = False
                    else:
                        self.hide()
                        self.hidden = True
                    #event.accept()
            elif event.key() == QtCore.Qt.Key_Return:
                    self.show()
                    #event.accept()
            else:
                    super(Dialog, self).keyPressEvent(event)
"""
