## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>
## Preston Brown <pbrown@redhat.com>

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
import gobject
import gtk
from netconfpkg.NC_functions import _
from netconfpkg.gui import sharedtcpip
from netconfpkg.gui.DeviceConfigDialog import DeviceConfigDialog
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect


modeList = [
    [ _("Auto") , "Auto" ],
    [ _("Ad-Hoc") , "Ad-Hoc"],
    [ _("Managed") , "Managed"],
    [ _("Master") , "Master"],
#    [ _("Repeater") , "Repeater"],
#    [ _("Secondary") , "Secondary"]
]

class wirelessConfigDialog(DeviceConfigDialog):
    def __init__(self, device):
        glade_file = "wirelessconfig.glade"

        self.initialized = False

        DeviceConfigDialog.__init__(self, glade_file, device)

        if not self.initialized:
            self.do_init()

    def do_init(self):
        # pylint: disable-msg=W0201        
        xml_signal_autoconnect(self.xml,
            {
            "on_essidAutoButton_toggled" : self.on_essidAutoButton_toggled,
            })

        window = self.sharedtcpip_xml.get_widget ('dhcpWindow')
        frame = self.sharedtcpip_xml.get_widget ('dhcpFrame')
        vbox = self.xml.get_widget ('generalVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.dhcp_init (self.sharedtcpip_xml, self.device)

        window = self.sharedtcpip_xml.get_widget ('routeWindow')
        frame = self.sharedtcpip_xml.get_widget ('routeFrame')
        vbox = self.xml.get_widget ('routeVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.route_init (self.sharedtcpip_xml, self.device, self.dialog)

        window = self.sharedtcpip_xml.get_widget ('hardwareWindow')
        frame = self.sharedtcpip_xml.get_widget ('hardwareFrame')
        vbox = self.xml.get_widget ('hardwareVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.hardware_init (self.sharedtcpip_xml, self.device)

        self.modestore = gtk.ListStore(gobject.TYPE_STRING,
                                    gobject.TYPE_STRING)
        for i in modeList:
            self.modestore.append(i)

        combo = self.xml.get_widget("modeCombo")
        combo.set_model(self.modestore)
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)

        self.xml.get_widget("rateCombo").set_popdown_strings((
            _("Auto"),
            "11M",
            "5.5M",
            "2M",
            "1M"
        ))

        combo.connect("changed", self.on_modeChanged)
        self.initialized = True

    def hydrate(self):
        if not self.initialized:
            self.do_init()

        DeviceConfigDialog.hydrate(self)

        sharedtcpip.dhcp_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.hardware_hydrate (self.sharedtcpip_xml, self.device)

        wl = self.device.Wireless
        if wl:
            if wl.Mode and self.modestore:
                values = [ r[1].lower() for r in self.modestore ]
                match_row = values.index(wl.Mode.lower())
                self.xml.get_widget("modeCombo").set_active(match_row)

            if wl.EssId == "":
                self.xml.get_widget("essidAutoButton").set_active(True)
                self.xml.get_widget("essidEntry").set_sensitive(False)
            else:
                self.xml.get_widget("essidSpecButton").set_active(True)
                self.xml.get_widget("essidAutoButton").set_active(False)
                self.xml.get_widget("essidEntry").set_sensitive(True)
            if wl.EssId:
                self.xml.get_widget("essidEntry").set_text(wl.EssId)

            if wl.Channel and wl.Channel != "":
                self.xml.get_widget("channelEntry").set_text(
                                                        wl.Channel)

            if wl.Rate:
                self.xml.get_widget("rateEntry").set_text(_(wl.Rate))

            if wl.Key: 
                self.xml.get_widget("keyEntry").set_text(wl.Key)

        self.on_modeChanged(self.xml.get_widget("modeEntry"))
        self.on_essidAutoButton_toggled(self.xml.get_widget("essidAutoButton"))


    def dehydrate(self):
        DeviceConfigDialog.dehydrate(self)
        sharedtcpip.dhcp_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.hardware_dehydrate (self.sharedtcpip_xml, self.device)

        wl = self.device.Wireless
        if wl:
            if self.xml.get_widget("essidAutoButton").get_active():
                wl.EssId = ""
            else:
                wl.EssId = self.xml.get_widget("essidEntry").get_text()

            row = self.xml.get_widget("modeCombo").get_active()
            wl.Mode = self.modestore[row][1]
            
            if wl.Mode == "Managed":
                wl.Channel = ""
                wl.Rate = "auto"
            else:
                channel = self.xml.get_widget("channelEntry").get_text()
                if channel == "Auto":
                    wl.Channel = ""
                else:
                    wl.Channel = channel

                rate = self.xml.get_widget("rateEntry").get_text()
                if rate == _("Auto"):
                    wl.Rate = "auto"
                else:
                    wl.Rate = rate
            # FIXME: [168036] check the key!
            wl.Key = self.xml.get_widget("keyEntry").get_text()

    def on_essidAutoButton_toggled(self, check):
        self.xml.get_widget("essidEntry").set_sensitive(not check.get_active())

    def on_modeChanged(self, entry): # pylint: disable-msg=W0613
        mode = self.modestore[self.xml.get_widget("modeCombo").get_active()][1]
        if mode == "Managed":
            self.xml.get_widget("channelCombo").set_sensitive(False)
            self.xml.get_widget("rateCombo").set_sensitive(False)
            self.xml.get_widget("rateEntry").set_sensitive(False)
        else:
            self.xml.get_widget("channelCombo").set_sensitive(True)
            self.xml.get_widget("rateCombo").set_sensitive(True)
            self.xml.get_widget("rateEntry").set_sensitive(True)
        self.on_essidAutoButton_toggled(self.xml.get_widget("essidAutoButton"))

def register_plugin():
    from netconfpkg.plugins import NCPluginDevWireless
    NCPluginDevWireless.setDevWirelessDialog(wirelessConfigDialog)

__author__ = "Harald Hoyer <harald@redhat.com>"
