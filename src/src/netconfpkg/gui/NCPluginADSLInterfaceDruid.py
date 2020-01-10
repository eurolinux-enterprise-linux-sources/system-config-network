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
import re
from netconfpkg import NCDeviceList, NCProfileList, NCHardwareList
from netconfpkg.NC_functions import (_, getNewDialupDevice, DSL,
    request_rpms)
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.EthernetHardwareDruid import ethernetHardware
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from netconfpkg.gui.InterfaceCreator import InterfaceCreator
from netconfpkg.gui.tonline import TonlineDialog
from netconfpkg.plugins import NCPluginDevADSL


# FIXME: [131556] system-config-network lacks support for pppoatm
class ADSLInterfaceDruid(InterfaceCreator):
    def __init__(self, toplevel=None, 
                 connection_type='Ethernet', do_save = 1, druid = None):
        InterfaceCreator.__init__(self, do_save = do_save)
        self.toplevel = toplevel
        self.topdruid = druid
        self.devicelist = NCDeviceList.getDeviceList()
        self.device = NCPluginDevADSL.DevADSL()
        self.profilelist = NCProfileList.getProfileList()
        self.toplevel = toplevel
        self.connection_type = connection_type
        self.druids = []
        self.xml = None
        self.druid = None

    def init_gui(self):
        if self.xml:
            return

        if request_rpms(["rp-pppoe"]):
            return

        glade_file = 'ADSLInterfaceDruid.glade'

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, 'druid', 
                                 domain=GUI_functions.PROGNAME)
        xml_signal_autoconnect(self.xml, 
            { 
            "on_dsl_config_page_back" : self.on_dsl_config_page_back, 
            "on_dsl_config_page_next" : self.on_dsl_config_page_next, 
            "on_dsl_config_page_prepare" : self.on_dsl_config_page_prepare, 
            "on_finish_page_finish" : self.on_finish_page_finish, 
            "on_finish_page_prepare" : self.on_finish_page_prepare, 
            "on_finish_page_back" : self.on_finish_page_back, 
            "on_providerNameEntry_insert_text" : (
                                self.on_generic_entry_insert_text,
                                r"^[a-z|A-Z|0-9\-_:]+$"), 
            "on_tonlineButton_clicked" : self.on_tonlineButton_clicked, 

              }
            )


        self.druid = self.xml.get_widget('druid')
        for i in self.druid.get_children():
            self.druid.remove(i)
            self.druids.append(i)

    def on_generic_entry_insert_text(self, entry, partial_text, length, 
                                     pos, mstr): # pylint: disable-msg=W0613
        text = partial_text[0:length]
        if re.match(mstr, text):
            return
        entry.emit_stop_by_name('insert_text')

    def get_project_name(self):
        return _('xDSL connection')

    def get_type(self):
        return DSL

    def get_project_description(self):
        return _(
        "Create an xDSL connection.  This is a connection that uses one of "
        "several types of broadband connections collective known as Digital "
        "Subscriber Lines.  This list includes ADSL (Asymmetric, faster "
        "downloads than uploads), IDSL (over an ISDN line for distance), SDSL "
        "(Symmetric, downloads and uploads at the same speed), and several "
        "others.  These types of connections are common in the United States, "
        "and are gaining acceptance elsewhere.  Speeds vary according to the "
        "technology used, but generally range from 144kbps to 1.0Mbps.")

    def get_druids(self):
        self.init_gui()
        hwDruid = ethernetHardware(self.toplevel)
        druid = hwDruid.get_druids()
        if druid: 
            return druid + self.druids[0:]
        else: return self.druids[0:]

    def on_dsl_config_page_back(self, druid_page, druid):
        pass

    def on_dsl_config_page_next(self, 
                                druid_page, druid): # pylint: disable-msg=W0613
        if self.check():
            self.dehydrate()
            return False
        else:
            return True

    def on_dsl_config_page_prepare(self, 
                            druid_page, druid): # pylint: disable-msg=W0613
        self.hydrate()

    def on_finish_page_back(self, 
                            druid_page, druid): # pylint: disable-msg=W0613
        self.devicelist.rollback() 

    def on_finish_page_prepare(self, 
                               druid_page, druid): # pylint: disable-msg=W0613
        hardwarelist = NCHardwareList.getHardwareList()
        for hw in hardwarelist:
            if hw.Type == self.connection_type:
                break

        dialup = self.device.Dialup
        # FIXME: Bad style for translation.. 
        s = str(_("You have selected the following information:") + "\n\n" 
                + "    " + _("Ethernet device:") + "  " + dialup.EthDevice 
                + "\n" + "    " + _("Provider name:") + "  " 
                + dialup.ProviderName + "\n" +  "    " 
                + _("Login name:") + "  " + dialup.Login)
        druid_page.set_text(s)

    def on_finish_page_finish(self, 
                              druid_page, druid): # pylint: disable-msg=W0613
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

        self.save()
        self.toplevel.destroy()
        gtk.main_quit()

    def check(self):
        return (len(self.xml.get_widget(
                    "providerNameEntry").get_text().strip()) > 0
           and len(self.xml.get_widget(
                    "loginNameEntry").get_text().strip()) > 0
           and len(self.xml.get_widget(
                    "passwordEntry").get_text().strip()) > 0
           and len(self.xml.get_widget(
                    "ethernetDeviceEntry").get_text().strip()) > 0)

    def hydrate(self):
        dialup = self.device.Dialup
        ecombo = self.xml.get_widget("ethernetDeviceComboBox")

        hwdesc = []
        hwcurr = None
        hardwarelist = NCHardwareList.getHardwareList()
        for hw in hardwarelist:
            if hw.Type == "Ethernet":
                desc = str(hw.Name) + ' (' + hw.Description + ')'
                hwdesc.append(desc)
                if dialup and dialup.EthDevice and \
                   hw.Name == dialup.EthDevice:
                    hwcurr = desc

        if len(hwdesc):
            hwdesc.sort()
            ecombo.set_popdown_strings(hwdesc)

        if not hwcurr and len(hwdesc):
            hwcurr = hwdesc[0]

        widget = self.xml.get_widget("ethernetDeviceEntry")
        if dialup and dialup.EthDevice:
            widget.set_text(hwcurr)
        #widget.set_position(0)

    def on_tonlineButton_clicked(self, *args): # pylint: disable-msg=W0613
        self.dehydrate()
        dialup = self.device.Dialup
        dialog = TonlineDialog(dialup.Login, dialup.Password)
        dl = dialog.xml.get_widget ("Dialog")

        dl.set_transient_for(self.toplevel)
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)

        if dl.run() != gtk.RESPONSE_OK:
            dl.destroy()
            return

        dl.destroy()
        dialup.Login = dialog.login
        dialup.Password = dialog.password
        self.xml.get_widget("loginNameEntry").set_text(dialup.Login)
        self.xml.get_widget("passwordEntry").set_text(dialup.Password)
        self.xml.get_widget("providerNameEntry").set_text("T-Online")

    def dehydrate(self):
        self.device.DeviceId = self.xml.get_widget(
                                'providerNameEntry').get_text()
        self.device.DeviceId = re.sub('-', '_', self.device.DeviceId)

        self.device.Type = 'xDSL'
        self.device.BootProto = 'dialup'
        self.device.AllowUser = True
        self.device.IPv6Init = False
        self.device.AutoDNS = True
        dialup = self.device.createDialup()
        hw = self.xml.get_widget("ethernetDeviceEntry").get_text()
        fields = hw.split()
        hw = fields[0]
        dialup.EthDevice = hw
        dialup.ProviderName = self.xml.get_widget(
                                "providerNameEntry").get_text()
        dialup.Login = self.xml.get_widget("loginNameEntry").get_text()
        dialup.Password = self.xml.get_widget("passwordEntry").get_text()
        dialup.SyncPPP = False
        self.device.Device = getNewDialupDevice(NCDeviceList.getDeviceList(),
                                                 self.device)
        dialup.DefRoute = True
        self.device.AutoDNS = True

def register_plugin():
    NCPluginDevADSL.setDevADSLWizard(ADSLInterfaceDruid)
    
__author__ = "Harald Hoyer <harald@redhat.com>"
