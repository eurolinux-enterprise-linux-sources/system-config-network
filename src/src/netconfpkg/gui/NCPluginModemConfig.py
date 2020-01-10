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
import gtk.glade
import os
from netconfpkg import NCHardwareList
from netconfpkg.NC_functions import modemDeviceList, _, modemFlowControls
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import load_icon, xml_signal_autoconnect


class modemDialog:
    def __init__(self, hw):
        glade_file = "modemconfig.glade"

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None,
                                 domain=GUI_functions.PROGNAME)

        xml_signal_autoconnect(self.xml,
            {
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked
            })

        self.dialog = self.xml.get_widget("Dialog")
        load_icon("network.xpm", self.dialog)

        self.hw = hw

        self.setup()
        self.hydrate()


    def on_Dialog_delete_event(self, *args):
        pass

    def on_okButton_clicked(self, button): # pylint: disable-msg=W0613
        self.dehydrate()

    def on_cancelButton_clicked(self, button):
        pass

    def setup(self):
        self.xml.get_widget(\
            "modemDeviceEntryCombo").set_popdown_strings(modemDeviceList)
        flowcontrols = []
        for i in modemFlowControls.keys():
            flowcontrols.append(modemFlowControls[i])
        self.xml.get_widget(\
            "flowControlCombo").set_popdown_strings(flowcontrols)

    def hydrate(self):
        if self.hw.Modem.DeviceName != None:
            if not self.hw.Modem.DeviceName in modemDeviceList:
                modemDeviceList.insert(0, self.hw.Modem.DeviceName)
                self.xml.get_widget(\
                    "modemDeviceEntryCombo").set_popdown_strings(\
                    modemDeviceList)
            self.xml.get_widget(\
                'modemDeviceEntry').set_text(self.hw.Modem.DeviceName)
        if self.hw.Modem.BaudRate != None:
            self.xml.get_widget(\
                'baudrateEntry').set_text(str(self.hw.Modem.BaudRate))
        if self.hw.Modem.FlowControl != None and \
               modemFlowControls.has_key(self.hw.Modem.FlowControl):
            self.xml.get_widget(\
                'flowControlEntry').set_text(\
                modemFlowControls[self.hw.Modem.FlowControl])
        if self.hw.Modem.ModemVolume != None:
            self.xml.get_widget('volumeMenu').set_history(\
                int(self.hw.Modem.ModemVolume))
        if self.hw.Modem.DialCommand != None:
            self.xml.get_widget('toneDialingCB').set_active(\
                self.hw.Modem.DialCommand == 'ATDT')

    def dehydrate(self):
        hardwarelist = NCHardwareList.getHardwareList()

        self.hw.Description = _('Generic Modem')

        modem_list = []
        if not self.hw.Name:
            for i in hardwarelist:
                if i.Type == "Modem":
                    modem_list.append(i.Name)
            if modem_list:
                for i in xrange(100):
                    if modem_list.count("Modem"+str(i)) == 0:
                        self.hw.Name = "Modem" + str(i)
                        break
            else:
                self.hw.Name = "Modem0"

        self.hw.Modem.DeviceName = self.xml.get_widget(\
            "modemDeviceEntry").get_text()
        self.hw.Modem.BaudRate = int(\
            self.xml.get_widget("baudrateEntry").get_text())

        flow = self.xml.get_widget("flowControlEntry").get_text()
        for i in modemFlowControls.keys():
            if modemFlowControls[i] == flow:
                self.hw.Modem.FlowControl = i
                break

        Item = self.xml.get_widget("volumeMenu").get_child().get_label()
        if Item == _("Off"):
            self.hw.Modem.ModemVolume = 0
        elif Item == _("Low"):
            self.hw.Modem.ModemVolume = 1
        elif Item == _("Medium"):
            self.hw.Modem.ModemVolume = 2
        elif Item == _("High"):
            self.hw.Modem.ModemVolume = 3
        elif Item == _("Very High"):
            self.hw.Modem.ModemVolume = 4
        else:
            self.hw.Modem.ModemVolume = 0

        if self.xml.get_widget("toneDialingCB").get_active():
            self.hw.Modem.DialCommand = "ATDT"
        else:
            self.hw.Modem.DialCommand = "ATDP"

        if len(self.hw.Modem.DeviceName)>5 and \
               self.hw.Modem.DeviceName[:5] != '/dev/':
            self.hw.Modem.DeviceName = '/dev/' + self.hw.Modem.DeviceName


def register_plugin():
    from netconfpkg.plugins import NCPluginHWModem
    NCPluginHWModem.setHwModemDialog(modemDialog)

__author__ = "Harald Hoyer <harald@redhat.com>"

