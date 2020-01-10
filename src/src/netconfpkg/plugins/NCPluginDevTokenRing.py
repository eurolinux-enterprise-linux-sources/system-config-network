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
from netconfpkg.NCDevice import Device
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NC_functions import TOKENRING, getDeviceType


_devTokenRingDialog = None
_devTokenRingWizard = None

class DevTokenRing(Device):
    def __init__(self):
        super(DevTokenRing, self).__init__()
        self.Type = TOKENRING

    def getDialog(self):
        if not _devTokenRingDialog:
            return None
        
        dialog =  _devTokenRingDialog(self)
        if hasattr(dialog, "xml"):
            return dialog.xml.get_widget("Dialog")

        return dialog

    def getWizard(self):
        return _devTokenRingWizard

    def isType(self, device):
        if device.Type == TOKENRING:
            return True
        if getDeviceType(device.Device) == TOKENRING:
            return True
        return False

def setDevTokenRingDialog(dialog):
    global _devTokenRingDialog  # pylint: disable-msg=W0603
    _devTokenRingDialog = dialog

def setDevTokenRingWizard(wizard):
    global _devTokenRingWizard  # pylint: disable-msg=W0603
    _devTokenRingWizard = wizard

def register_plugin():
    __df = getDeviceFactory()
    __df.register(DevTokenRing, TOKENRING)

__author__ = "Harald Hoyer <harald@redhat.com>"
