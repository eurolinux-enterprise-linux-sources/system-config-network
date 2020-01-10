"Wireless Hardware Device Plugin"
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
from netconfpkg.NCHardware import Hardware
from netconfpkg.NCHardwareFactory import getHardwareFactory
from netconfpkg.NC_functions import WIRELESS, getHardwareType


_hwEthernetDialog = None
_hwEthernetWizard = None

class HwWireless(Hardware):
    "Wireless Hardware Device Class"

    def __init__(self):
        super(HwWireless, self).__init__()
        self.Type = WIRELESS

    def getDialog(self):
        """
        returns a gtk dialog
        """
        if _hwEthernetDialog == None: 
            return None
        return _hwEthernetDialog(self).xml.get_widget("Dialog")

    def getWizard(self):
        """
        returns a gtk wizard
        """
        return _hwEthernetWizard

    def isType(self, hardware):
        """
        check if device is of type ISDN
        """
        if hardware.Type == WIRELESS:
            return True
        if getHardwareType(hardware.Hardware) == WIRELESS:
            return True
        return False

    def save(self):
        self.saveModule()

    def save(self):
        self.saveModule()

def setHwWirelessDialog(dialog):
    """
    Set the gtk Modem Dialog
    """
    global _hwEthernetDialog  # pylint: disable-msg=W0603
    _hwEthernetDialog = dialog

def setHwWirelessWizard(wizard):
    """
    Set the gtk Modem Wizard
    """
    global _hwEthernetWizard # pylint: disable-msg=W0603
    _hwEthernetWizard = wizard

def register_plugin():
    __df = getHardwareFactory()
    __df.register(HwWireless, WIRELESS)

__author__ = "Harald Hoyer <harald@redhat.com>"
