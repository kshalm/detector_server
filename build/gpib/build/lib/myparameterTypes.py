from __future__ import print_function
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.python2_3 import asUnicode
from pyqtgraph.parametertree.Parameter import Parameter, registerParameterType
#from .ParameterItem import ParameterItem
#from pyqtgraph.widgets.SpinBox import SpinBox
#from pyqtgraph.widgets.ColorButton import ColorButton
#from pyqtgraph.widgets.GradientWidget import GradientWidget ## creates import loop
#import pyqtgraph as pg
import pyqtgraph.pixmaps as pixmaps
import os
from pyqtgraph.pgcollections import OrderedDict

from pyqtgraph.parametertree.parameterTypes import WidgetParameterItem


class MyListParameterItem(WidgetParameterItem):
    """
    WidgetParameterItem subclass providing comboBox that lets the user select from a list of options.
    
    """

    def __init__(self, param, depth):
        self.targetValue = None
        WidgetParameterItem.__init__(self, param, depth)
        print('Using mylist')

    def makeWidget(self):
        opts = self.param.opts
        t = opts['type']
        w = QtGui.QComboBox()
        w.setMaximumHeight(
            20)  ## set to match height of spin box and line edit
        """
        w.sigChanged = w.currentIndexChanged 
        w.value = self.value
        w.setValue = self.setValue
        """
        ww = QtGui.QWidget()
        self.setupBtn = QtGui.QPushButton('Setup')
        self.setupBtn.clicked.connect(self.clicked)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(w)
        layout.addWidget(self.setupBtn)
        #self.w = w
        #  Stuff below is a hack... I should make a new object that inherts from QComboBox so that I don't have
        #     to remap so much by hand... Hopefully I got everything... If not, should spend time working on the inheritance
        ww.setLayout(layout)
        ww.sigChanged = w.currentIndexChanged
        ww.value = self.value
        ww.setValue = self.setValue
        ww.findText = w.findText
        ww.setCurrentIndex = w.setCurrentIndex
        ww.clear = w.clear
        ww.addItem = w.addItem
        ww.currentText = w.currentText
        ww.blockSignals = w.blockSignals
        ww.count = w.count
        self.widget = ww  ## needs to be set before limits are changed
        self.limitsChanged(self.param, self.param.opts['limits'])
        if len(self.forward) > 0:
            self.setValue(self.param.value())
        return ww

    def clicked(self):
        print('clicked setup button')
        self.param.activate()

    def value(self):
        key = asUnicode(self.widget.currentText())

        return self.forward.get(key, None)

    def setValue(self, val):
        self.targetValue = val
        if val not in self.reverse[0]:
            self.widget.setCurrentIndex(0)
        else:
            key = self.reverse[1][self.reverse[0].index(val)]
            ind = self.widget.findText(key)
            self.widget.setCurrentIndex(ind)

    def limitsChanged(self, param, limits):
        # set up forward / reverse mappings for name:value

        if len(limits) == 0:
            limits = [
                ''
            ]  ## Can never have an empty list--there is always at least a singhe blank item.

        self.forward, self.reverse = MyListParameter.mapping(limits)
        try:
            self.widget.blockSignals(True)
            val = self.targetValue  #asUnicode(self.widget.currentText())

            self.widget.clear()
            for k in self.forward:
                self.widget.addItem(k)
                if k == val:
                    self.widget.setCurrentIndex(self.widget.count() - 1)
                    self.updateDisplayLabel()
        finally:
            self.widget.blockSignals(False)


class MyListParameter(Parameter):
    itemClass = MyListParameterItem
    sigActivated = QtCore.Signal(object)

    def __init__(self, **opts):
        self.forward = OrderedDict()  ## {name: value, ...}
        self.reverse = ([], [])  ## ([value, ...], [name, ...])

        ## Parameter uses 'limits' option to define the set of allowed values
        if 'values' in opts:
            opts['limits'] = opts['values']
        if opts.get('limits', None) is None:
            opts['limits'] = []
        Parameter.__init__(self, **opts)
        self.setLimits(opts['limits'])

    def setLimits(self, limits):
        self.forward, self.reverse = self.mapping(limits)

        Parameter.setLimits(self, limits)
        #print self.name(), self.value(), limits
        if len(self.reverse) > 0 and self.value() not in self.reverse[0]:
            self.setValue(self.reverse[0][0])

    def activate(self):
        self.sigActivated.emit(self)
        self.emitStateChanged('activated', None)

    #def addItem(self, name, value=None):
    #if name in self.forward:
    #raise Exception("Name '%s' is already in use for this parameter" % name)
    #limits = self.opts['limits']
    #if isinstance(limits, dict):
    #limits = limits.copy()
    #limits[name] = value
    #self.setLimits(limits)
    #else:
    #if value is not None:
    #raise Exception  ## raise exception or convert to dict?
    #limits = limits[:]
    #limits.append(name)
    ## what if limits == None?

    @staticmethod
    def mapping(limits):
        ## Return forward and reverse mapping objects given a limit specification
        forward = OrderedDict()  ## {name: value, ...}
        reverse = ([], [])  ## ([value, ...], [name, ...])
        if isinstance(limits, dict):
            for k, v in list(limits.items()):
                forward[k] = v
                reverse[0].append(v)
                reverse[1].append(k)
        else:
            for v in limits:
                n = asUnicode(v)
                forward[n] = v
                reverse[0].append(v)
                reverse[1].append(n)
        return forward, reverse


registerParameterType('mylist', MyListParameter, override=True)
