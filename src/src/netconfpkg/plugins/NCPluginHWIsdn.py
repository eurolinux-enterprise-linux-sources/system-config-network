"ISDN Hardware Device Plugin"
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
from netconfpkg.NCHardware import Hardware, Card
from netconfpkg.NCHardwareFactory import getHardwareFactory
from netconfpkg.NC_functions import ISDN, getHardwareType


_hwIsdnDialog = None
_hwIsdnWizard = None

class HwIsdn(Hardware):
    "ISDN Hardware Device Class"
    def __init__(self):
        super(HwIsdn, self).__init__()
        self.Type = ISDN
        self.Card = Card()
        self.Card.ChannelProtocol = "2"

    def getDialog(self):
        """
        returns a gtk dialog
        """
        if _hwIsdnDialog == None:
            return None
        return _hwIsdnDialog(self).xml.get_widget("Dialog")

    def getWizard(self):
        """
        returns a gtk wizard
        """
        return _hwIsdnWizard

    def isType(self, hardware):
        """
        check if device is of type ISDN
        """
        if hardware.Type == ISDN:
            return True
        if getHardwareType(hardware.Hardware) == ISDN:
            return True
        return False

    def save(self, *args, **kwargs): # pylint: disable-msg=W0613
        """
        save the ISDN configuration
        """
        import netconfpkg.NCisdnhardware
        isdn = netconfpkg.NCisdnhardware.ConfISDN()

        
        isdn.Description = self.Description
        isdn.Type = self.Card.Type
        isdn.ModuleName = self.Card.ModuleName
        isdn.IRQ = self.Card.IRQ
        isdn.IoPort = self.Card.IoPort
        isdn.IoPort1 = self.Card.IoPort1 
        isdn.IoPort2 = self.Card.IoPort2 
        isdn.Mem = self.Card.Mem 
        isdn.ChannelProtocol = self.Card.ChannelProtocol
        isdn.Firmware = self.Card.Firmware
        isdn.DriverId = self.Card.DriverId
        isdn.VendorId = self.Card.VendorId
        isdn.DeviceId = self.Card.DeviceId
        isdn.save()


def setHwIsdnDialog(dialog):
    """
    Set the gtk Modem Dialog
    """
    global _hwIsdnDialog  # pylint: disable-msg=W0603
    _hwIsdnDialog = dialog

def setHwIsdnWizard(wizard):
    """
    Set the gtk Modem Wizard
    """
    global _hwIsdnWizard  # pylint: disable-msg=W0603
    _hwIsdnWizard = wizard


def register_plugin():
    __df = getHardwareFactory()
    __df.register(HwIsdn, ISDN)

__author__ = "Harald Hoyer <harald@redhat.com>"
