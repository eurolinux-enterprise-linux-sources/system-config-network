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
from netconfpkg import NCHardwareList, NC_functions
from netconfpkg.gui import sharedtcpip
from netconfpkg.gui.DeviceConfigDialog import DeviceConfigDialog
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect


class tokenringConfigDialog(DeviceConfigDialog):
    def __init__(self, device):
        glade_file = "tokenringconfig.glade"
        DeviceConfigDialog.__init__(self, glade_file, device)
        xml_signal_autoconnect(self.xml,
            {
            "on_aliasSupportCB_toggled" : self.on_aliasSupportCB_toggled,
#            "on_hwAddressCB_toggled" : self.on_hwAddressCB_toggled,
#            "on_hwProbeButton_clicked" : self.on_hwProbeButton_clicked,
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

    def hydrate(self):
        DeviceConfigDialog.hydrate(self)
        sharedtcpip.dhcp_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_hydrate (self.sharedtcpip_xml, self.device)

        ecombo = self.xml.get_widget("tokenringDeviceComboBox")
        hwlist = NCHardwareList.getHardwareList()
        (hwcurr, hwdesc) = NC_functions.create_tokenring_combo(hwlist, 
                                                        self.device.Device)

        if len(hwdesc):
            ecombo.set_popdown_strings(hwdesc)

        widget = self.xml.get_widget("tokenringDeviceEntry")
        if self.device.Device:
            widget.set_text(hwcurr)
        #widget.set_position(0)

        if self.device.Alias != None:
            self.xml.get_widget("aliasSupportCB").set_active(True)
            self.xml.get_widget("aliasSpinBox").set_value(self.device.Alias)
        else:
            self.xml.get_widget("aliasSupportCB").set_active(False)

    def dehydrate(self):
        DeviceConfigDialog.dehydrate(self)
        sharedtcpip.dhcp_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_dehydrate (self.sharedtcpip_xml, self.device)

        hw = self.xml.get_widget("tokenringDeviceEntry").get_text()
        fields = hw.split()
        hw = fields[0]
        self.device.Device = hw
        if self.xml.get_widget("aliasSupportCB").get_active():
            self.device.Alias = self.xml.get_widget(
                                    "aliasSpinBox").get_value_as_int()
        else:
            self.device.Alias = None

    def on_aliasSupportCB_toggled(self, check):
        self.xml.get_widget("aliasSpinBox").set_sensitive(check.get_active())

def register_plugin():
    from netconfpkg.plugins import NCPluginDevTokenRing
    NCPluginDevTokenRing.setDevTokenRingDialog(tokenringConfigDialog)

__author__ = "Harald Hoyer <harald@redhat.com>"
