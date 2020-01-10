"Modem Interface Plugin"

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
from netconfpkg.NCDialup import ModemDialup
from netconfpkg.NC_functions import MODEM, getDeviceType
from netconfpkg.gdt import (gdtstruct_properties)


_devModemDialog = None
_devModemWizard = None

ModemList = None
def getModemList():
    # FIXME: [165331] Can't detect external modem on /dev/ttyS0
    # move to plugins!
    global ModemList
    if ModemList:
        return ModemList[:]

    ModemList = []

# FIXME: find another way to detect modems
#    import kudzu
#    # pylint: disable-msg=E1101
#    res = kudzu.probe(kudzu.CLASS_MODEM, 
#                      kudzu.BUS_UNSPEC, 
#                      kudzu.PROBE_ALL)   
#    if res != []:
#        for v in res:
#            dev = str(v.device)
#            if dev and dev != 'None':
#                ModemList.append('/dev/' + dev)
    return ModemList[:]

class DevModem(Device):
    gdtstruct_properties([
                          ('Dialup', ModemDialup, "Test doc string"),
                          ])
    
    def __init__(self):
        super(DevModem, self).__init__()
        self.Type = MODEM
        self.Dialup = ModemDialup()

    def load(self, name): # pylint: disable-msg=W0613
        """
        load(devicename)
        load a modem definition
        """
        conf = ConfDevice(name)
        Device.load(self, name)
        self.Dialup.load(conf, self)
        
    def save(self):
        super(DevModem, self).save()
        conf = ConfDevice(self.DeviceId)
        self.Dialup.save(conf, self.DeviceId, self.oldname)
        conf.write()        

    def createDialup(self):
        """
        create a ModemDialup instance for self.Dialup
        """
        if (self.Dialup == None
            or (not isinstance(self.Dialup, ModemDialup))):
            self.Dialup = ModemDialup()
        return self.Dialup

    def getDialog(self):
        """
        returns a gtk dialog
        """
        dialog =  _devModemDialog(self)
        if hasattr(dialog, "xml"):
            return dialog.xml.get_widget("Dialog")

        return dialog

    def getWizard(self):
        """
        returns a gtk wizard
        """
        return _devModemWizard

    def isType(self, device):
        """
        check if device is of type MODEM
        """
        if device.Type == MODEM:
            return True
        if getDeviceType(device.Device) == MODEM:
            return True
        return False

    def getHWDevice(self):
        """
        get the Hardware Device this Interface belongs to
        """
        if self.Dialup:
            return self.Dialup.Inherits

        return None

def setDevModemDialog(dialog):
    """
    Set the gtk Modem Dialog
    """
    global _devModemDialog  # pylint: disable-msg=W0603
    _devModemDialog = dialog

def setDevModemWizard(wizard):
    """
    Set the gtk Modem Wizard
    """
    global _devModemWizard  # pylint: disable-msg=W0603
    _devModemWizard = wizard

def register_plugin():
    __df = getDeviceFactory()
    __df.register(DevModem, MODEM)

__author__ = "Harald Hoyer <harald@redhat.com>"
