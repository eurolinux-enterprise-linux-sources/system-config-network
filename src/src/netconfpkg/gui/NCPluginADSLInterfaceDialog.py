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
import gtk
from netconfpkg.NCDialup import DM_AUTO, DM_MANUAL
from netconfpkg.gui import sharedtcpip
from netconfpkg.gui.DeviceConfigDialog import DeviceConfigDialog
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from netconfpkg.gui.tonline import TonlineDialog


# FIXME: [131556] system-config-network lacks support for pppoatm
class ADSLInterfaceDialog(DeviceConfigDialog):
    def __init__(self, device):
        glade_file = "ADSLInterfaceDialog.glade"
        DeviceConfigDialog.__init__(self, glade_file,
                                    device)

        xml_signal_autoconnect(self.xml, {
            "on_tonlineButton_clicked" : self.on_tonlineButton_clicked,
            "on_dialonDemandCB_clicked" : self.on_dialonDemandCB_clicked,
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
        sharedtcpip.dsl_hardware_init (self.sharedtcpip_xml, self.device)
        self.hydrate ()

    def hydrate(self):
        DeviceConfigDialog.hydrate(self)
        dialup = self.device.Dialup
        widget = self.xml.get_widget("providerNameEntry")
        if dialup.ProviderName:
            widget.set_text(dialup.ProviderName)
        #widget.set_position(0)

        widget = self.xml.get_widget("loginNameEntry")
        if dialup.Login:
            widget.set_text(dialup.Login)
        #widget.set_position(0)

        widget =  self.xml.get_widget("passwordEntry")
        if dialup.Password:
            widget.set_text(dialup.Password)
        #widget.set_position(0)

        widget = self.xml.get_widget("serviceNameEntry")
        if dialup.ServiceName:
            widget.set_text(dialup.ServiceName)
        #widget.set_position(0)

        widget = self.xml.get_widget("acNameEntry")
        if dialup.AcName:
            widget.set_text(dialup.AcName)
        #widget.set_position(0)


        if dialup.Persist:
            self.xml.get_widget("persistCB").set_active(dialup.Persist)

        if dialup.DialMode:
            self.xml.get_widget("dialonDemandCB").set_active(\
                dialup.DialMode == DM_AUTO)
            self.xml.get_widget("idleTimeSB").set_text(\
                str(dialup.HangupTimeout))
            self.on_dialonDemandCB_clicked()
        self.xml.get_widget("useSyncpppCB").set_active(dialup.SyncPPP == True)

        self.xml.get_widget("defrouteCB").set_active(dialup.DefRoute == True)

        sharedtcpip.dhcp_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_hydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.dsl_hardware_hydrate (self.sharedtcpip_xml, self.device)


    def dehydrate(self):
        DeviceConfigDialog.dehydrate(self)
        dialup = self.device.Dialup
        dialup.ProviderName = self.xml.get_widget(
                                "providerNameEntry").get_text()
        dialup.Login = self.xml.get_widget("loginNameEntry").get_text()
        dialup.Password = self.xml.get_widget("passwordEntry").get_text()
        dialup.ServiceName = self.xml.get_widget("serviceNameEntry").get_text()
        dialup.AcName = self.xml.get_widget("acNameEntry").get_text()
        dialup.SyncPPP = self.xml.get_widget("useSyncpppCB").get_active()
        dialup.DefRoute = self.xml.get_widget("defrouteCB").get_active()
        dialup.Persist = self.xml.get_widget("persistCB").get_active()
        if self.xml.get_widget("dialonDemandCB").get_active():
            dialup.DialMode = DM_AUTO
            dialup.HangupTimeout = int(self.xml.get_widget(
                                        "idleTimeSB").get_text())
        else:
            dialup.DialMode = DM_MANUAL

        if not self.device.Device:
            self.device.Device = "dsl"
        sharedtcpip.dhcp_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.route_dehydrate (self.sharedtcpip_xml, self.device)
        sharedtcpip.dsl_hardware_dehydrate (self.sharedtcpip_xml, self.device)

    def on_dialonDemandCB_clicked(self, *args): # pylint: disable-msg=W0613
        self.xml.get_widget("idleTimeSB").set_sensitive(\
            self.xml.get_widget("dialonDemandCB").get_active())

    def on_tonlineButton_clicked(self, *args): # pylint: disable-msg=W0613
        self.dehydrate()
        dialup = self.device.Dialup
        dialog = TonlineDialog(dialup.Login, dialup.Password)
        dl = dialog.xml.get_widget ("Dialog")

        dl.set_transient_for(self.dialog)
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)

        if dl.run() != gtk.RESPONSE_OK:
            dl.destroy()
            return

        dl.destroy()
        dialup.Login = dialog.login
        dialup.Password = dialog.password
        self.hydrate()
        
def register_plugin():
    from netconfpkg.plugins import NCPluginDevADSL
    NCPluginDevADSL.setDevADSLDialog(ADSLInterfaceDialog)

__author__ = "Harald Hoyer <harald@redhat.com>"
