# -*- coding: utf-8 -*-
## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>
## Copyright (C) 2001, 2002 Trond Eivind Glomsrød <teg@redhat.com>

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
from netconfpkg.NC_functions import (request_rpms, _,
                                    MODEM, generic_error_dialog,
                                    modemFlowControls, modemDeviceList, 
                                    CRTSCTS)
from netconfpkg.gui.DialupDruid import DialupDruid
from netconfpkg.gui.GUI_functions import (xml_signal_autoconnect,
                                          GLADEPATH, NETCONFDIR,
                                          PROGNAME)
from netconfpkg.plugins.NCPluginDevModem import getModemList
from netconfpkg.gui.InterfaceCreator import InterfaceCreator


class ModemInterfaceWizard(InterfaceCreator):
    modemList = None
    def __init__ (self, toplevel=None, do_save = 1, druid = None):
        InterfaceCreator.__init__(self, do_save = do_save)
        self.do_save = do_save
        self.toplevel = toplevel
        self.hardwarelist = NCHardwareList.getHardwareList()
        self.hw = None
        self.druids = []
        self.xml = None

    def init_gui(self):
        if self.xml:
            return True

        if request_rpms(["ppp", "wvdial"]):
            return False

        glade_file = 'ModemDruid.glade'

        if not os.path.isfile(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, 'druid', domain=PROGNAME)
        xml_signal_autoconnect(self.xml, 
            {
            "on_Modem_prepare" : self.on_Modem_prepare, 
            "on_Modem_back" : self.on_Modem_back, 
            "on_Modem_next" : self.on_Modem_next, 
            })


        druid = self.xml.get_widget('druid')
        for I in druid.get_children():
            druid.remove(I)
            self.druids.append(I)

        self.setup()

        return True

    def get_project_name(self):
        return _('Modem connection')

    def get_type(self):
        return MODEM

    def get_project_description (self):
        return _(
        "Create a new Modem connection.  This is a connection that uses a "
        "serial analog modem to dial into to your Internet Service Provider. "
        "These modems use sound over a normal copper telephone line to "
        "transmit data. These types of connections are available just about "
        "anywhere in the world where there is a phone system."
        )


    def get_druids(self):
        if not self.init_gui():
            return []

        Type = MODEM
        dialup = DialupDruid(self.toplevel, Type, 
                                         do_save = self.do_save)
        for self.hw in self.hardwarelist:
            if self.hw.Type == Type: 
                return dialup.get_druids()

        mid = self.hardwarelist.addHardware(Type)
        self.hw = self.hardwarelist[mid]
        self.hw.Type = Type
        self.hw.Name = Type + '0'
        if Type == 'ISDN':  
            self.hw.createCard()
        elif Type == 'Modem': 
            self.hw.createModem()

        return self.druids[0:] + dialup.get_druids()

    def on_Modem_prepare(self, druid_page, druid):
        if not ModemInterfaceWizard.modemList:
            # FIXME: [165331] Can't detect external modem on /dev/ttyS0
            dialog = gtk.Dialog(_('Modem probing...'), 
                                None, 
                                gtk.DIALOG_MODAL|gtk.DIALOG_NO_SEPARATOR
                                |gtk.DIALOG_DESTROY_WITH_PARENT)
            dialog.set_border_width(10)
            label = gtk.Label(_('Probing for Modems, please wait...'))
            dialog.vbox.pack_start(label, False)  # pylint: disable-msg=E1101
            dialog.set_transient_for(self.toplevel)
            dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            dialog.set_modal(True)
            label.show_now()
            dialog.show_all()
            dialog.show_now()
            gtk.gdk.flush()
            while gtk.events_pending():
                gtk.main_iteration(False)
            dlist = getModemList()
            ModemInterfaceWizard.modemList = dlist
            dialog.destroy()
            if dlist == []:
                generic_error_dialog(_('No modem was found on your system.'), 
                                     self.toplevel)
                dlist = modemDeviceList
            ModemInterfaceWizard.modemList = dlist
        else:
            dlist = ModemInterfaceWizard.modemList

        self.xml.get_widget("modemDeviceEntryComBo").set_popdown_strings(dlist)
        # 460800 seems to be to high
        self.xml.get_widget("baudrateEntry").set_text("115200")
        self.xml.get_widget(\
                'flowControlEntry').set_text(\
                modemFlowControls[CRTSCTS])

    def on_Modem_next(self, druid_page, druid):
        self.dehydrate()

    def on_Modem_back(self, druid_page, druid):
        self.hardwarelist.rollback() 

    def setup(self):
        flowcontrols = []
        for i in modemFlowControls.keys():
            flowcontrols.append(modemFlowControls[i])
        self.xml.get_widget(\
            "flowControlCombo").set_popdown_strings(flowcontrols)

    def dehydrate(self):
        self.hw.Description = _('Generic Modem')
        self.hw.Modem.DeviceName = self.xml.get_widget(
                                        "modemDeviceEntry").get_text()
        if (len(self.hw.Modem.DeviceName) > 5 
            and self.hw.Modem.DeviceName[:5] != '/dev/'):
            self.hw.Modem.DeviceName = str('/dev/' 
                            + self.hw.Modem.DeviceName )
        self.hw.Modem.BaudRate = int(
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

    def hydrate(self):
        hardwarelist = NCHardwareList.getHardwareList()

        if self.hw.Modem.DeviceName != None:
            if not self.hw.Modem.DeviceName in modemDeviceList:
                modemDeviceList.insert(0, self.hw.Modem.DeviceName)
                self.xml.get_widget(
                    "modemDeviceEntryCombo").set_popdown_strings(
                                                modemDeviceList)
            self.xml.get_widget('modemDeviceEntry').set_text(
                                            self.hw.Modem.DeviceName)
        if self.hw.Modem.BaudRate != None:
            self.xml.get_widget('baudrateEntry').set_text(
                                                str(self.hw.Modem.BaudRate))
        if (self.hw.Modem.FlowControl != None 
            and modemFlowControls.has_key(self.hw.Modem.FlowControl)):
            self.xml.get_widget(
                'flowControlEntry').set_text(
                modemFlowControls[self.hw.Modem.FlowControl])
        else:
            self.xml.get_widget(
                'flowControlEntry').set_text(
                modemFlowControls[CRTSCTS])


def register_plugin():
    from netconfpkg.plugins import NCPluginDevModem
    NCPluginDevModem.setDevModemWizard(ModemInterfaceWizard)
    
__author__ = "Harald Hoyer <harald@redhat.com>"
