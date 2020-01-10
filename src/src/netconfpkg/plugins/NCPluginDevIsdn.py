## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
from netconfpkg.NCDevice import Device, ConfDevice
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NCDialup import IsdnDialup
from netconfpkg.NC_functions import (_, ISDN, generic_run_dialog,
                                     getDeviceType)
from netconfpkg.gdt import gdtstruct_properties


_devIsdnDialog = None
_devIsdnWizard = None

class DevIsdn(Device):
    gdtstruct_properties([
                          ('Dialup', IsdnDialup, "Test doc string"),
                          ])
    
    def __init__(self):
        super(DevIsdn, self).__init__()
        self.Type = ISDN
        self.Dialup = IsdnDialup()

    def load(self, name): # pylint: disable-msg=W0613
        Device.load(self, name)
        conf = ConfDevice(name)
        self.Dialup.load(conf, self)
        
    def save(self):
        super(DevIsdn, self).save()
        conf = ConfDevice(self.DeviceId)
        self.Dialup.save(conf, self.DeviceId, self.oldname)
        conf.write()        

    def createDialup(self):
        if (self.Dialup == None) \
               or not isinstance(self.Dialup, IsdnDialup):
            self.Dialup = IsdnDialup()
        return self.Dialup

    def getDialog(self):
        dialog = _devIsdnDialog(self)
        if hasattr(dialog, "xml"):
            return dialog.xml.get_widget("Dialog")

        return dialog

    def getWizard(self):
        return _devIsdnWizard

    def isType(self, device):
        if device.Type == ISDN:
            return True
        if getDeviceType(device.Device) == ISDN:
            return True
        return False

    def getHWDevice(self):
        # FIXME: Support more than one ISDN Card
        return "ISDN Card 0"

    def activate(self, dialog = None):
        command = '/bin/sh'
        param = [ command,
                  "-c",
                  "/sbin/ifup %s; /usr/sbin/userisdnctl %s dial" % \
                  (self.DeviceId, self.DeviceId) ]

        try:
            (ret, msg) =  generic_run_dialog(\
                command,
                param,
                catchfd = (1, 2),
                title = _('Network device activating...'),
                label = _('Activating network device %s, '
                          'please wait...') % (self.DeviceId),
                errlabel = _('Cannot activate '
                             'network device %s!\n') % (self.DeviceId),
                dialog = dialog)

        except RuntimeError, msg:
            ret = -1

        return ret, msg

    def deactivate(self, dialog = None):
        command = '/bin/sh'
        param = [ command,
                  "-c",
                  "/usr/sbin/userisdnctl %s hangup ;/sbin/ifdown %s;" % \
                  (self.DeviceId, self.DeviceId) ]

        try:
            (ret, msg) =  generic_run_dialog(\
                command,
                param,
                catchfd = (1, 2),
                title = _('Network device deactivating...'),
                label = _('Deactivating network device %s, '
                          'please wait...') % (self.DeviceId),
                errlabel = _('Cannot deactivate '
                             'network device %s!\n') % (self.DeviceId),
                dialog = dialog)

        except RuntimeError, msg:
            ret = -1

        return ret, msg

def setDevIsdnDialog(dialog):
    global _devIsdnDialog  # pylint: disable-msg=W0603
    _devIsdnDialog = dialog

def setDevIsdnWizard(wizard):
    global _devIsdnWizard  # pylint: disable-msg=W0603
    _devIsdnWizard = wizard

def register_plugin():
    df = getDeviceFactory()
    df.register(DevIsdn, ISDN)
    
__author__ = "Harald Hoyer <harald@redhat.com>"