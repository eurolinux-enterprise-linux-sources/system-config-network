"QETH Hardware Device Plugin"
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
from netconfpkg.NC_functions import QETH, getHardwareType


_hwQethDialog = None
_hwQethWizard = None

class HwQeth(Hardware):    
    "QETH Hardware Device Class"
    def __init__(self):
        super(HwQeth, self).__init__()
        self.Type = QETH
        self.Card = Card()  
        self.Description = "Qeth Device"
        
    def getDialog(self):
        """
        returns a gtk dialog
        """
        if _hwQethDialog == None:
            return None
        if hasattr(_hwQethDialog, 'getDialog'):
            return _hwQethDialog(self).getDialog()
        return _hwQethDialog(self).xml.get_widget("Dialog")
    
    def getWizard(self):
        """
        returns a gtk wizard
        """
        return _hwQethWizard
    
    def save(self, *args, **kwargs): # pylint: disable-msg=W0613
        """
        save the configuration
        """
        self.saveModule()

    def isType(self, hardware):
        """
        check if device is of type QETH
        """
        if hardware.Type == QETH:
            return True
        if getHardwareType(hardware.Hardware) == QETH:
            return True
        return False

def setHwQethDialog(dialog):
    """
    Set the gtk Dialog
    """
    global _hwQethDialog # pylint: disable-msg=W0603
    _hwQethDialog = dialog
    
def setHwQethWizard(wizard):
    """
    Set the gtk Wizard
    """
    global _hwQethWizard # pylint: disable-msg=W0603
    _hwQethWizard = wizard
    
def register_plugin():
    import os
    machine = os.uname()[4]
    if machine == 's390' or machine == 's390x':
        __df = getHardwareFactory()
        __df.register(HwQeth, QETH)
    
__author__ = "Harald Hoyer <harald@redhat.com>"


