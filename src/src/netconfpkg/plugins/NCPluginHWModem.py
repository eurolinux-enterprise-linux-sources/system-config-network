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
from netconfpkg.NC_functions import MODEM, getHardwareType
from netconfpkg.gdt import (Gdtstruct, gdtstruct_properties, Gdtstr,
                            Gdtint)


_hwModemDialog = None
_hwModemWizard = None

# FIXME: [177472] Speedtouch USB 330 modem not recognised

class Modem(Gdtstruct):
    gdtstruct_properties([
                          ('DeviceName', Gdtstr, "Test doc string"),
                          ('BaudRate', Gdtint, "Test doc string"),
                          ('FlowControl', Gdtstr, "Test doc string"),
                          ('ModemVolume', Gdtint, "Test doc string"),
                          ('DialCommand', Gdtstr, "Test doc string"),
                          ('InitString', Gdtstr, "Test doc string"),
                          ])
    def __init__(self):
        super(Modem, self).__init__()
        self.DeviceName = None
        self.BaudRate = None
        self.FlowControl = None
        self.ModemVolume = None
        self.DialCommand = None
        self.InitString = None

class HwModem(Hardware):
    gdtstruct_properties([
                          ('Modem', Modem, "Test doc string"),
                          ])

    def __init__(self):
        super(HwModem, self).__init__()
        self.Modem = Modem()
        self.Type = MODEM
        
    def createModem(self):
        return self.Modem
    
    def getDialog(self):
        if _hwModemDialog == None: 
            return None
        return _hwModemDialog(self).xml.get_widget("Dialog")

    def getWizard(self):
        return _hwModemWizard

    def isType(self, hardware):
        if hardware.Type == MODEM:
            return True
        if getHardwareType(hardware.Hardware) == MODEM:
            return True
        return False

    def save(self, *args, **kwargs): # pylint: disable-msg=W0613
        from netconfpkg.NCHardwareList import getMyWvDial
        
        wvdial = getMyWvDial(create_if_missing = True)
        wvdial[self.Name]['Modem'] = self.Modem.DeviceName
        if self.Modem.BaudRate:
            wvdial[self.Name]['Baud'] = str(self.Modem.BaudRate)
        if not self.Modem.ModemVolume:
            self.Modem.ModemVolume = 0
        wvdial[self.Name]['SetVolume'] = str(self.Modem.ModemVolume)
        if self.Modem.DialCommand:
            wvdial[self.Name]['Dial Command'] = str(self.Modem.DialCommand)
        if not self.Modem.InitString: 
            self.Modem.InitString = 'ATZ'
        wvdial[self.Name]['Init1'] = str(self.Modem.InitString)
        if self.Modem.ModemVolume == 0:
            wvdial[self.Name]['Init3'] = 'ATM0'
        else:
            wvdial[self.Name]['Init3'] = 'ATM1L' + str(self.Modem.ModemVolume)

        if self.Modem.FlowControl:
            wvdial[self.Name]['FlowControl'] = str(self.Modem.FlowControl)

def setHwModemDialog(dialog):
    global _hwModemDialog  # pylint: disable-msg=W0603
    _hwModemDialog = dialog

def setHwModemWizard(wizard):
    global _hwModemWizard  # pylint: disable-msg=W0603
    _hwModemWizard = wizard

def register_plugin():
    __df = getHardwareFactory()
    __df.register(HwModem, MODEM)

__author__ = "Harald Hoyer <harald@redhat.com>"
