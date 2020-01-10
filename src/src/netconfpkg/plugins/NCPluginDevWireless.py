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
from netconfpkg.NCWireless import Wireless
from netconfpkg.NC_functions import WIRELESS, getDeviceType
from netconfpkg.gdt import (gdtstruct_properties)


# FIXME: add detection method for Wireless HW
# FIXME: [190317] Dell Wireless 1390 802.11g Mini Card doesn't work
# FIXME: [183272] system-config-network unable to see 
# cisco pcmcia wireless card using airo driver


class DevWireless(Device):
    gdtstruct_properties([
                          ('Wireless', Wireless, "Test doc string"),
                          ])
    
    def __init__(self):
        super(DevWireless, self).__init__()
        self.Type = WIRELESS
        self.Wireless = Wireless()

    def load(self, name):
        super(DevWireless, self).load(name)
        conf = ConfDevice(name)
        self.Wireless.load(conf, self.DeviceId)
        del conf

    def save(self):
        super(DevWireless, self).save()
        conf = ConfDevice(self.DeviceId)
        conf.fsf()
        self.Wireless.save(conf, self.DeviceId)
        conf.write()
        del conf

    def createWireless(self):
        return self.Wireless

    def getDialog(self):
        if not _devWirelessDialog:
            return None

        dialog =  _devWirelessDialog(self)
        if hasattr(dialog, "xml"):
            return dialog.xml.get_widget("Dialog")

        return dialog

    def getWizard(self):
        return _devWirelessWizard

    def isType(self, device):
        if device.Type == WIRELESS:
            return True
        if getDeviceType(device.Device) == WIRELESS:
            return True
        return False

_devWirelessDialog = None
_devWirelessWizard = None

def setDevWirelessDialog(dialog):
    global _devWirelessDialog  # pylint: disable-msg=W0603
    _devWirelessDialog = dialog

def setDevWirelessWizard(wizard):
    global _devWirelessWizard  # pylint: disable-msg=W0603
    _devWirelessWizard = wizard

def register_plugin():
    __df = getDeviceFactory()
    __df.register(DevWireless, WIRELESS)

__author__ = "Harald Hoyer <harald@redhat.com>"
