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
from netconfpkg import NCisdnhardware
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import load_icon, xml_signal_autoconnect


class isdnHardwareDialog:
    def __init__(self, hw):
        glade_file = "isdnhardware.glade"

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, 
                                 domain=GUI_functions.PROGNAME)

        xml_signal_autoconnect(self.xml,
            {
            "on_isdnCardEntry_changed" : self.on_isdnCardEntry_changed,
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked
            })

        self.hw = hw
        self.cardname = ""
        self.dialog = self.xml.get_widget("Dialog")
        load_icon("network.xpm", self.dialog)

        self.setup()
        self.hydrate()

    def on_Dialog_delete_event(self, *args):
        pass

    def on_okButton_clicked(self, button): # pylint: disable-msg=W0613
        self.dehydrate()

    def on_cancelButton_clicked(self, button):
        pass

    def on_isdnCardEntry_changed(self, entry):
        cardname = entry.get_text()
        card = NCisdnhardware.ConfISDN()
        card.get_resource(cardname)

        if card.IRQ:
            self.xml.get_widget("irqSpinButton").set_sensitive(True)
            self.xml.get_widget("irqSpinButton").set_value(int(card.IRQ))
        else:
            self.xml.get_widget("irqSpinButton").set_sensitive(False)

        if card.Mem:
            self.xml.get_widget("memEntry").set_sensitive(True)
            self.xml.get_widget("memEntry").set_text(card.Mem)
        else:
            self.xml.get_widget("memEntry").set_sensitive(False)

        if card.IoPort:
            self.xml.get_widget("ioEntry").set_sensitive(True)
            self.xml.get_widget("ioEntry").set_text(card.IoPort)
        else:
            self.xml.get_widget("ioEntry").set_sensitive(False)

        if card.IoPort1:
            self.xml.get_widget("io1Entry").set_sensitive(True)
            self.xml.get_widget("io1Entry").set_text(card.IoPort1)
        else:
            self.xml.get_widget("io1Entry").set_sensitive(False)

        if card.IoPort2:
            self.xml.get_widget("io2Entry").set_sensitive(True)
            self.xml.get_widget("io2Entry").set_text(card.IoPort2)
        else:
            self.xml.get_widget("io2Entry").set_sensitive(False)

    def hydrate(self):
        has_card = False
        hw = self.hw

        if not hw.Name:
            conf = NCisdnhardware.ConfISDN()
            new_card = conf.detect()
            if new_card:
                has_card = True
                self.cardname = new_card.keys()[0]
                conf.get_resource(self.cardname)
                hw.Card.ChannelProtocol = conf.ChannelProtocol
                hw.Card.IRQ = conf.IRQ
                hw.Card.Mem = conf.Mem
                hw.Card.IoPort = conf.IoPort
                hw.Card.IoPort1 = conf.IoPort1
                hw.Card.IoPort2 = conf.IoPort2
        else:
            has_card = True

        if has_card:
            if hw.Card.ChannelProtocol == '2':
                self.xml.get_widget("euroIsdnButton").set_active(True)
            else:
                self.xml.get_widget("1tr6Button").set_active(True)

            if self.hw.Description:
                self.xml.get_widget("adapterEntry").set_text(
                                                    self.hw.Description)

            if hw.Card.IRQ:
                self.xml.get_widget("irqSpinButton").set_sensitive(True)
                self.xml.get_widget("irqSpinButton").set_value(int(hw.Card.IRQ))
            else:
                self.xml.get_widget("irqSpinButton").set_sensitive(False)

            if hw.Card.Mem:
                self.xml.get_widget("memEntry").set_sensitive(True)
                self.xml.get_widget("memEntry").set_text(hw.Card.Mem)
            else:
                self.xml.get_widget("memEntry").set_sensitive(False)

            if hw.Card.IoPort:
                self.xml.get_widget("ioEntry").set_sensitive(True)
                self.xml.get_widget("ioEntry").set_text(hw.Card.IoPort)
            else:
                self.xml.get_widget("ioEntry").set_sensitive(False)

            if hw.Card.IoPort1:
                self.xml.get_widget("io1Entry").set_sensitive(True)
                self.xml.get_widget("io1Entry").set_text(hw.Card.IoPort1)
            else:
                self.xml.get_widget("io1Entry").set_sensitive(False)

            if hw.Card.IoPort2:
                self.xml.get_widget("io2Entry").set_sensitive(True)
                self.xml.get_widget("io2Entry").set_text(hw.Card.IoPort2)
            else:
                self.xml.get_widget("io2Entry").set_sensitive(False)

    def dehydrate(self):
        isdncard = NCisdnhardware.ConfISDN()
        isdncard.get_resource(self.xml.get_widget('adapterEntry').get_text())

        self.hw.Name = "ISDN Card 0"
        self.hw.Description = isdncard.Description
        self.hw.Card.ModuleName = isdncard.ModuleName
        self.hw.Card.Type = isdncard.Type
        self.hw.Card.Firmware = isdncard.Firmware
        self.hw.Card.VendorId = isdncard.VendorId
        self.hw.Card.DeviceId = isdncard.DeviceId
        self.hw.Card.DriverId = isdncard.DriverId

        if self.xml.get_widget("euroIsdnButton").get_active():
            self.hw.Card.ChannelProtocol = '2'
        else:
            self.hw.Card.ChannelProtocol = '1'

        if not self.xml.get_widget('irqSpinButton').get_property("sensitive"):
            self.hw.Card.IRQ = isdncard.IRQ
        else:
            self.hw.Card.IRQ = str(self.xml.get_widget(
                                    'irqSpinButton').get_value_as_int())

        if not self.xml.get_widget('memEntry').get_property("sensitive"):
            self.hw.Card.Mem = isdncard.Mem
        else:
            self.hw.Card.Mem = self.xml.get_widget('memEntry').get_text()

        if not self.xml.get_widget('ioEntry').get_property("sensitive"):
            self.hw.Card.IoPort = isdncard.IoPort
        else:
            self.hw.Card.IoPort = self.xml.get_widget('ioEntry').get_text()

        if not self.xml.get_widget('io1Entry').get_property("sensitive"):
            self.hw.Card.IoPort1 = isdncard.IoPort1
        else:
            self.hw.Card.IoPort1 = self.xml.get_widget('io1Entry').get_text()

        if not self.xml.get_widget('io2Entry').get_property("sensitive"):
            self.hw.Card.IoPort2 = isdncard.IoPort2
        else:
            self.hw.Card.IoPort2 = self.xml.get_widget('io2Entry').get_text()

    def setup(self):
        # pylint: disable-msg=W0212
        cardlist = NCisdnhardware._card.keys()
        cardlist.sort()
        self.xml.get_widget("isdnCardComboBox").set_popdown_strings(cardlist)

def register_plugin():
    from netconfpkg.plugins import NCPluginHWIsdn
    NCPluginHWIsdn.setHwIsdnDialog(isdnHardwareDialog)
    
__author__ = "Harald Hoyer <harald@redhat.com>"
