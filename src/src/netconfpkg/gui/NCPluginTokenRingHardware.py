## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>

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
from netconfpkg import NCHardwareList
from netconfpkg.NC_functions import _,  generic_longinfo_dialog
from netconfpkg.gui.GUI_functions import gui_run_dialog
from netconfpkg.gui.HardwareDialog import HardwareDialog


class TokenringHardwareDialog(HardwareDialog):
    def __init__(self, hw):
        HardwareDialog.__init__(self, hw,
                                "tokenringhardware.glade",
                                {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked,
            "on_adapterEntry_changed" : self.on_adapterEntry_changed
            })

        self.button = 0

    def on_okButton_clicked(self, button):
        HardwareDialog.on_okButton_clicked(self, button)
        cmd = [ '/sbin/modprobe ', self.hw.Card.ModuleName ]
        if self.hw.Card.IRQ:
            cmd.append(' irq='+self.hw.Card.IRQ)
        if self.hw.Card.IoPort:
            cmd.append(' io='+self.hw.Card.IoPort)
        if self.hw.Card.IoPort1:
            cmd.append(' io1='+self.hw.Card.IoPort1)
        if self.hw.Card.IoPort2:
            cmd.append(' io2='+self.hw.Card.IoPort2)
        if self.hw.Card.Mem:
            cmd.append(' mem='+self.hw.Card.Mem)
        if self.hw.Card.DMA0:
            cmd.append(' dma='+str(self.hw.Card.DMA0))
        if self.hw.Card.DMA1:
            cmd.append(' dma1='+str(self.hw.Card.DMA1))

        (status, output) = gui_run_dialog('/sbin/modprobe', cmd,
                                          catchfd = (1, 2), 
                                          dialog = self.dialog)
        if status != 0:
            generic_longinfo_dialog(
                _('The Token Ring card could not be initialized. '
                  'Please verify your settings and try again.'),
                output, self.dialog)

    def on_cancelButton_clicked(self, button):
        #self.button = 1
        pass

    def on_adapterEntry_changed(self, entry):
        pass

    def hydrate(self):
        HardwareDialog.hydrate(self)

        if self.hw.Name:
            self.xml.get_widget('tokenringDeviceEntry').set_text(self.hw.Name)
            self.xml.get_widget('adapterEntry').set_text(self.hw.Description)
            self.xml.get_widget('adapterEntry').set_sensitive(False)
            self.xml.get_widget('adapterComboBox').set_sensitive(False)

    def setup(self):
        HardwareDialog.setup(self)

        mlist = []
        modInfo = NCHardwareList.getModInfo()
        for i in modInfo.keys():
            if modInfo[i]['type'] == "tr" and \
                   modInfo[i].has_key('description'):
                mlist.append(modInfo[i]['description'])
        mlist.sort()
        self.xml.get_widget("adapterComboBox").set_popdown_strings(mlist)
        nextdev = NCHardwareList.getNextDev("tr")
        self.xml.get_widget('tokenringDeviceEntry').set_text(nextdev)

    def dehydrate(self):
        HardwareDialog.dehydrate(self)

        self.hw.Name = self.xml.get_widget('tokenringDeviceEntry').get_text()
        self.hw.Description = self.xml.get_widget('adapterEntry').get_text()
        self.hw.Type = 'Token Ring'
        self.hw.createCard()
        modInfo = NCHardwareList.getModInfo()
        if not self.hw.Card.ModuleName or self.hw.Card.ModuleName == "":
            self.hw.Card.ModuleName = _('Unknown')
        for i in modInfo.keys():
            if modInfo[i].has_key('description') and \
                   modInfo[i]['description'] == self.hw.Description:
                self.hw.Card.ModuleName = i


def register_plugin():
    from netconfpkg.plugins import NCPluginHWTokenring
    NCPluginHWTokenring.setHwTokenringDialog(TokenringHardwareDialog)

__author__ = "Harald Hoyer <harald@redhat.com>"    
