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
import gobject
import gtk.glade
import os
from netconfpkg import NCDeviceList, NCProfileList, NCHardwareList
from netconfpkg.NC_functions import (_, WIRELESS, NETCONFDIR, PROGNAME, 
                                     request_rpms)
from netconfpkg.gui import sharedtcpip
from netconfpkg.gui.EthernetHardwareDruid import ethernetHardware
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect, GLADEPATH
from netconfpkg.gui.InterfaceCreator import InterfaceCreator
from netconfpkg.plugins import NCPluginDevWireless
import ethtool


modeList = [
    [ _("Auto") , "Auto" ],
    [ _("Ad-Hoc") , "Ad-Hoc"],
    [ _("Managed") , "Managed"],
    [ _("Master") , "Master"],
#    [ _("Repeater") , "Repeater"],
#    [ _("Secondary") , "Secondary"]
]

class WirelessInterfaceWizard(InterfaceCreator):
    def __init__(self, toplevel=None, connection_type=WIRELESS, do_save = 1,
                 druid = None):
        InterfaceCreator.__init__(self, do_save = do_save)
        self.toplevel = toplevel
        self.topdruid = druid
        self.xml = None
        self.devicelist = NCDeviceList.getDeviceList()
        self.device = NCPluginDevWireless.DevWireless()
        self.device.Type = connection_type
        self.device.OnBoot = False
        self.device.AllowUser = False
        self.device.IPv6Init = False

        self.profilelist = NCProfileList.getProfileList()
        self.toplevel = toplevel
        self.connection_type = connection_type
        self.hw_sel = 0
        self.hwPage = False
        self.druids = []
        self.devlist = []

    def init_gui(self):
        # pylint: disable-msg=W0201
        if self.xml:
            return

        if request_rpms(["wireless-tools"]):
            return

        glade_file = "sharedtcpip.glade"
        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file
        self.sharedtcpip_xml = gtk.glade.XML(glade_file, None,
                                                 domain=PROGNAME)

        glade_file = 'WirelessInterfaceDruid.glade'

        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, 'druid', domain=PROGNAME)
        xml_signal_autoconnect(self.xml,
            { "on_hostname_config_page_back" : \
              self.on_hostname_config_page_back,
              "on_hostname_config_page_next" : \
              self.on_hostname_config_page_next,
              "on_hostname_config_page_prepare" : \
              self.on_hostname_config_page_prepare,
              "on_wireless_config_page_back" : \
              self.on_wireless_config_page_back,
              "on_wireless_config_page_next" : \
              self.on_wireless_config_page_next,
              "on_wireless_config_page_prepare" : \
              self.on_wireless_config_page_prepare,
              "on_hw_config_page_back" : self.on_hw_config_page_back,
              "on_hw_config_page_next" : self.on_hw_config_page_next,
              "on_hw_config_page_prepare" : self.on_hw_config_page_prepare,
              "on_finish_page_finish" : self.on_finish_page_finish,
              "on_finish_page_prepare" : self.on_finish_page_prepare,
              "on_finish_page_back" : self.on_finish_page_back,
              "on_essidAutoButton_toggled" : self.on_essidAutoButton_toggled,
              }
            )



        window = self.sharedtcpip_xml.get_widget ('dhcpWindow')
        frame = self.sharedtcpip_xml.get_widget ('dhcpFrame')
        vbox = self.xml.get_widget ('generalVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.dhcp_init (self.sharedtcpip_xml, self.device)

        self.druid = self.xml.get_widget('druid')
        for i in self.druid.get_children():
            self.druid.remove(i)
            self.druids.append(i)

        self.hwDruid = ethernetHardware(self.toplevel)
        self.hwDruid.has_ethernet = None
        self.druids = [self.druids[0]] + self.hwDruid.druids[:]\
                      + self.druids[1:]

        self.modestore = gtk.ListStore(gobject.TYPE_STRING,
                                    gobject.TYPE_STRING)
        for i in modeList:
            self.modestore.append(i)

        combo = self.xml.get_widget("modeCombo")
        combo.set_model(self.modestore)
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)
        combo.set_active(0)

        self.xml.get_widget("rateCombo").set_popdown_strings((
            _("Auto"),
            "11M",
            "5.5M",
            "2M",
            "1M"
        ))


    def get_project_name(self):
        return _('Wireless connection')

    def get_type(self):
        return WIRELESS

    def get_project_description(self):
        return _("Create a new wireless connection.")

    def get_druids(self):
        self.init_gui()
        return self.druids

    def on_hostname_config_page_back(self, druid_page, druid):
        pass

    def on_hostname_config_page_next(self, druid_page, druid):
        sharedtcpip.dhcp_dehydrate (self.sharedtcpip_xml, self.device)
        #self.device.Hostname = self.xml.get_widget("hostnameEntry").get_text()

    def on_hostname_config_page_prepare(self, druid_page, druid):
        sharedtcpip.dhcp_hydrate (self.sharedtcpip_xml, self.device)

    def on_wireless_config_page_back(self, druid_page, druid):
        childs = self.topdruid.get_children()
        if self.hwPage:
            self.topdruid.set_page(childs[2])
        else:
            self.topdruid.set_page(childs[1])
        return True

    def on_wireless_config_page_next(self, druid_page, druid):
        self.device.createWireless()
        wl = self.device.Wireless 

        if self.xml.get_widget("essidAutoButton").get_active():
            wl.EssId = ""
        else:
            wl.EssId = self.xml.get_widget("essidEntry").get_text()
        row = self.xml.get_widget("modeCombo").get_active()
        wl.Mode = self.modestore[row][1]

        rate = self.xml.get_widget("rateEntry").get_text()
        if wl.Mode == _("Managed"):
            wl.Channel = ""
            wl.Rate = "auto"
        else:
            wl.Rate = rate
            channel = self.xml.get_widget("channelComboEntry").get_text()
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

    def on_wireless_config_page_prepare(self, druid_page, druid):
        if self.hwPage:
            self.device.Device = self.hwDruid.hw.Name
            self.device.Alias = None

        if self.device.Device != None:
            try:
                import iwlib
                info = iwlib.get_iwconfig(self.device.Device)
            except:
                pass
            else:
                if info.has_key("Mode"):
                    values = [ r[1].lower() for r in self.modestore ]
                    match_row = values.index(info["Mode"].lower())
                    self.xml.get_widget("modeCombo").set_active(match_row)

                if info.has_key("ESSID") and info["ESSID"] != "":
                    self.xml.get_widget("essidSpecButton").set_active(True)
                    self.xml.get_widget("essidEntry").set_sensitive(True)
                    self.xml.get_widget("essidEntry").set_text(info["ESSID"])
                else:
                    self.xml.get_widget("essidAutoButton").set_active(True)
                    self.xml.get_widget("essidEntry").set_sensitive(False)

                if info.has_key("Frequency") and info["Frequency"] < 1000:
                    self.xml.get_widget("channelCombo").set_text(
                                                        int(info["Frequency"]))

                if info.has_key("BitRate"):
                    self.xml.get_widget("rateEntry").set_text(
                                                        _(info["BitRate"]))

                if info.has_key("Key") and info["Key"] != "off":
                    self.xml.get_widget("keyEntry").set_text(info["Key"])

        self.on_modeChanged(self.xml.get_widget("modeCombo"))
        self.on_essidAutoButton_toggled(self.xml.get_widget("essidAutoButton"))

        self.xml.get_widget("modeCombo").connect("changed",
                                                 self.on_modeChanged)

    def on_modeChanged(self, entry):
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

    def on_essidAutoButton_toggled(self, check):
        self.xml.get_widget("essidEntry").set_sensitive(not check.get_active())

    def on_hw_config_page_back(self, druid_page, druid):
        pass

    def on_hw_config_page_next(self, druid_page, druid):
        clist = self.xml.get_widget("hardwareList")

        childs = self.topdruid.get_children()

        if not len(clist.selection):
            self.topdruid.set_page(childs[1])
            return True

        self.hw_sel = clist.selection[0]

        if (self.hw_sel + 1) == clist.rows:
            self.hwPage = True
            self.topdruid.set_page(childs[2])
        else:
            self.hwPage = False
            self.device.Device = self.devlist[clist.selection[0]]
            self.device.Alias = self.getNextAlias(self.device)
            self.topdruid.set_page(childs[3])

        return True

    def on_hw_config_page_prepare(self, druid_page, druid):
        hardwarelist = NCHardwareList.getHardwareList()
        hardwarelist.updateFromSystem()

        clist = self.xml.get_widget("hardwareList")
        clist.clear()
        self.devlist = []
        for hw in hardwarelist:
            if hw.Type == WIRELESS:
                desc = hw.Description + " (" + hw.Name + ")"
                clist.append([desc])
                self.devlist.append(hw.Name)

        clist.append([_("Other Wireless Card")])
        clist.select_row (self.hw_sel, 0)

    def on_finish_page_back(self, druid_page, druid):
        pass

    def on_finish_page_prepare(self, druid_page, druid):
        self.device.DeviceId = self.device.Device
        wl = self.device.Wireless 

        if self.device.Alias:
            self.device.DeviceId = self.device.DeviceId + ":" \
                                   + str(self.device.Alias)

        try: 
            hwaddr = ethtool.get_hwaddr(self.device.Device)
        except IOError, err:
            pass
        else:
            self.device.HardwareAddress = hwaddr

        # FIXME: Bad style for translation
        s = _("You have selected the following information:") + "\n\n"\
            + _("Device:") + " " + str(self.device.DeviceId) + " "

        hardwarelist = NCHardwareList.getHardwareList()
        for hw in hardwarelist:
            if hw.Name == self.device.Device:
                s = s + "(" + hw.Description + ")"
                break

        s = s + "\n"

        if (self.device.BootProto == "static" 
            or self.device.BootProto == "none"):
            s = s + str(_("Address:") + " " + (self.device.IP or '') + "\n"
            + _("Subnet mask:") + " " + (self.device.Netmask or '') + "\n"
            + _("Default gateway address:") + " " + (self.device.Gateway or '')
            + "\n")
        else:
            s = s + str(_("Automatically obtain IP address settings with:") 
                        + " " + self.device.BootProto + "\n")

        s = s + _("Mode:") + " " + str(wl.Mode) + "\n"
        s = s + _("ESSID (network ID):") + " "
        if not wl.EssId:
            s = s + _("Automatic") + "\n"
        else:
            s = s + str(wl.EssId) + "\n"
        if wl.Mode != "Managed":
            s = s + _("Channel:") + " " + str(wl.Channel) + "\n"
        s = s + str(_("Transmit rate:") + " " + str(wl.Rate) + "\n" 
                    + _("Key: "))


        if wl.Key:
            s = s + str(wl.Key) + "\n"
        else:
            s = s + _("encryption disabled") + "\n"

        druid_page.set_text(s)

    def on_finish_page_finish(self, druid_page, druid):
        
        hardwarelist = NCHardwareList.getHardwareList()
        hardwarelist.commit() 
        self.devicelist.append(self.device)
        self.device.commit()
        for prof in self.profilelist:
            if prof.Active == False:
                continue
            prof.ActiveDevices.append(self.device.DeviceId)
            break
        self.profilelist.commit()
        self.devicelist.commit()

        self.toplevel.destroy()
        gtk.main_quit()

def register_plugin():
    NCPluginDevWireless.setDevWirelessWizard(WirelessInterfaceWizard)
    
__author__ = "Harald Hoyer <harald@redhat.com>"
