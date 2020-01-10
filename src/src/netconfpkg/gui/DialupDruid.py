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
from gtk import CTREE_LINES_DOTTED
from netconfpkg import (NCDeviceList, NCProfileList, NCDeviceFactory,
    NCHardwareList, NCDialup)
from netconfpkg.NC_functions import (_, ISDN, MODEM, getNewDialupDevice, 
                                     NETCONFDIR, PROGNAME)
from netconfpkg.gui import GUI_functions, providerdb
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect
from netconfpkg.gui.InterfaceCreator import InterfaceCreator
from netconfpkg.gui.tonline import TonlineDialog

# pylint: disable-msg=E1103

class DialupDruid(InterfaceCreator):
    def __init__ (self, toplevel=None, connection_type=ISDN, 
                  do_save = 1, druid = None): 
        InterfaceCreator.__init__(self, do_save = do_save)

        self.connection_type = connection_type
        df = NCDeviceFactory.getDeviceFactory()
        self.device = df.getDeviceClass(connection_type)()
        self.toplevel = toplevel
        self.druids = []
        self.country = ""
        self.city = ""
        self.name = ""
        self.provider = None
        self.device.BootProto = 'dialup'
        self.device.AutoDNS = True

        self.devicelist = NCDeviceList.getDeviceList()
        self.profilelist = NCProfileList.getProfileList()
        self.xml = None
        self.druid = druid
        self.dbtree = None

    def get_project_name(self):
        pass

    def get_type(self):
        pass

    def get_project_description(self):
        pass


    def init_gui(self):
        if self.xml:
            return

        glade_file = 'DialupDruid.glade'
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, 'druid', 
                                 domain=PROGNAME)
        xml_signal_autoconnect(self.xml, 
            { "on_dialup_page_prepare" : self.on_dialup_page_prepare, 
              "on_dialup_page_next" : self.on_dialup_page_next, 
              "on_dhcp_page_prepare" : self.on_dhcp_page_prepare, 
              "on_dhcp_page_next" : self.on_dhcp_page_next, 
              "on_finish_page_finish" : self.on_finish_page_finish, 
              "on_finish_page_prepare" : self.on_finish_page_prepare, 
              "on_finish_page_back" : self.on_finish_page_back, 
              "on_ipAutomaticRadio_toggled" : self.on_ipBootProto_toggled, 
              "on_ipStaticRadio_toggled" : self.on_ipBootProto_toggled, 
              "on_sync_ppp_activate" : self.on_sync_ppp_activate, 
              "on_raw_ip_activate" : self.on_raw_ip_activate, 
              "on_providerNameEntry_insert_text" : \
              (self.on_generic_entry_insert_text, r"^[a-z|A-Z|0-9\-_:]+$"), 
              "on_tonlineButton_clicked" : self.on_tonlineButton_clicked, 
              }
            )

        self.druid = self.xml.get_widget ('druid')
        for I in self.druid.get_children():
            self.druid.remove (I)
            self.druids.append (I)


        # get the widgets we need
        self.dbtree = self.xml.get_widget("providerTree")

        self.setup_provider_db()

    def on_generic_entry_insert_text(self, entry, partial_text, length, 
                                     pos, mstr): # pylint: disable-msg=W0613
        text = partial_text[0:length]
        if re.match(mstr, text):
            return
        entry.emit_stop_by_name('insert_text')

    def get_druids (self):
        self.init_gui()
        return self.druids[0:]

    def on_dialup_page_next(self, 
                            druid_page, druid): # pylint: disable-msg=W0613
        if self.check():
            self.dehydrate()
            return False
        else:
            return True

    def on_ipBootProto_toggled(self, widget):
        if widget.name == "ipAutomaticRadio":
            active = widget.get_active()
        else:
            active = not widget.get_active()

        self.xml.get_widget('dhcpSettingFrame').set_sensitive(active)
        self.xml.get_widget('ipSettingFrame').set_sensitive(not active)

    def dhcp_hydrate (self, xml, device):
        if device.IP:
            xml.get_widget('ipAddressEntry').set_text(device.IP)
        else:
            xml.get_widget('ipAddressEntry').set_text('')
        if device.Netmask:
            xml.get_widget('ipNetmaskEntry').set_text(device.Netmask)
        else:
            xml.get_widget('ipNetmaskEntry').set_text('')
        if device.Gateway:
            xml.get_widget('ipGatewayEntry').set_text(device.Gateway)
        else:
            xml.get_widget('ipGatewayEntry').set_text('')

        xml.get_widget('dnsSettingCB').set_active(device.AutoDNS == True)

        if device.BootProto == "static" or device.BootProto == "none":
            xml.get_widget('ipAutomaticRadio').set_active(False)
            xml.get_widget('ipStaticRadio').set_active(True)
            self.on_ipBootProto_toggled(\
                xml.get_widget('ipAutomaticRadio'))
        else:
            device.BootProto = 'dialup'
            xml.get_widget('ipAutomaticRadio').set_active(True)
            xml.get_widget('ipStaticRadio').set_active(False)
            self.on_ipBootProto_toggled(\
                xml.get_widget('ipStaticRadio'))

    def dhcp_dehydrate (self, xml, device):
        if xml.get_widget('ipAutomaticRadio').get_active():
            device.BootProto = 'dialup'
            device.IP = ''
            device.Netmask = ''
            device.Gateway = ''
            device.Hostname = ''
            device.AutoDNS = xml.get_widget('dnsSettingCB').get_active()
        else:
            device.BootProto = 'none'
            device.IP = xml.get_widget('ipAddressEntry').get_text()
            device.Netmask = xml.get_widget('ipNetmaskEntry').get_text()
            device.Gateway = xml.get_widget('ipGatewayEntry').get_text()
            device.Hostname = ''
            
    def on_sync_ppp_activate(self, *args): # pylint: disable-msg=W0613
        self.xml.get_widget('ipAutomaticRadio').set_active(True)
        self.xml.get_widget('ipStaticRadio').set_active(False)
        self.xml.get_widget('ipAutomaticRadio').set_sensitive(True)
        self.on_ipBootProto_toggled(\
                self.xml.get_widget('ipStaticRadio'))
        dialup = self.device.createDialup()
        dialup.EncapMode = 'syncppp'
        self.device.Device = getNewDialupDevice(NCDeviceList.getDeviceList(), 
                                                self.device)

    def on_raw_ip_activate(self, *args): # pylint: disable-msg=W0613
        self.xml.get_widget('ipAutomaticRadio').set_active(False)
        self.xml.get_widget('ipStaticRadio').set_active(True)
        self.on_ipBootProto_toggled(\
                self.xml.get_widget('ipAutomaticRadio'))
        self.xml.get_widget('ipAutomaticRadio').set_sensitive(False)
        dialup = self.device.createDialup()
        dialup.EncapMode = 'rawip'
        self.device.Device = getNewDialupDevice(NCDeviceList.getDeviceList(), 
                                                self.device)

    def on_dhcp_page_back(self, druid_page, druid): # pylint: disable-msg=W0613
        return True

    def on_dhcp_page_next(self, druid_page, druid): # pylint: disable-msg=W0613
        self.dhcp_dehydrate(self.xml, self.device)

    def on_dhcp_page_prepare(self, 
                             druid_page, druid): # pylint: disable-msg=W0613
        self.dhcp_hydrate(self.xml, self.device)
        dialup = self.device.createDialup() 
        if self.connection_type == ISDN:
            if dialup.EncapMode == 'rawip':
                self.on_raw_ip_activate()
            else:
                self.on_sync_ppp_activate()
        else:
            self.xml.get_widget('encapModeMenu').set_sensitive(False)

    def on_finish_page_back(self, 
                            druid_page, druid): # pylint: disable-msg=W0613
        self.devicelist.rollback() 

    def on_dialup_page_prepare(self, 
                               druid_page, druid): # pylint: disable-msg=W0613
        self.setup()
        self.xml.signal_connect("on_providerTree_tree_select_row", 
                                self.on_providerTree_tree_select_row)

    def on_finish_page_prepare(self, 
                               druid_page, druid): # pylint: disable-msg=W0613
        hardwarelist = NCHardwareList.getHardwareList()
        description = ""        
        for hw in hardwarelist:
            if hw.Type == self.connection_type:
                description = hw.Description
                break
        dialup = self.device.createDialup() 

        s = _("You have selected the following information:") + \
            "\n\n" + "    " + \
            _("Hardware:") + "  " + description + "\n" + "    " + \
            _("Provider name:") + "  " + dialup.ProviderName + \
            "\n" +  "    " + \
            _("Login name:") + "  " + dialup.Login + "\n" +  "    " + \
            _("Phone number:") + "  " + dialup.PhoneNumber

        druid_page.set_text(s)

    def on_finish_page_finish(self, 
                              druid_page, druid): # pylint: disable-msg=W0613
        self.device.Device = getNewDialupDevice(NCDeviceList.getDeviceList(), 
                                                self.device)
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

    def setup(self):
        if not self.provider:
            self.xml.get_widget('druid').set_buttons_sensitive(\
                False, False, False, False)
        else:
            self.xml.get_widget('druid').set_buttons_sensitive(\
                False, True, True, False)
            self.xml.get_widget('areaCodeEntry').set_text(\
                self.provider['Areacode'])
            self.xml.get_widget('phoneEntry').set_text(\
                self.provider['PhoneNumber'])
            self.xml.get_widget('providerName').set_text(\
                self.provider['ProviderName'])
            if self.provider['Login']:
                self.xml.get_widget('dialupLoginNameEntry').set_text(\
                self.provider['Login'])
            if self.provider['Password']:
                self.xml.get_widget('dialupPasswordEntry').set_text(\
                self.provider['Password'])

    def check(self):
        return (len(self.xml.get_widget(\
            'phoneEntry').get_text().strip()) > 0 \
           and len(self.xml.get_widget(\
            'providerName').get_text().strip()) > 0 \
           and len(self.xml.get_widget(\
            'dialupLoginNameEntry').get_text().strip()) > 0 \
           and len(self.xml.get_widget(\
            'dialupPasswordEntry').get_text().strip()) > 0)

    def on_providerTree_tree_select_row(self, 
                                        ctree, 
                                        node, 
                                        column): # pylint: disable-msg=W0613
        node = ctree.selection[0]
        if len(node.children) == 0:
            try:
                self.country = ctree.get_node_info(node.parent.parent)[0]
                self.city = ctree.get_node_info(node.parent)[0]
                self.name = ctree.get_node_info(node)[0]
                self.provider = self.get_provider()
                self.setup()
            except(TypeError, AttributeError): # pylint: disable-msg=W0704
                pass

    def get_provider_list(self):
        return providerdb.get_provider_list(self.connection_type)

    def get_provider(self):
        isp_list = self.get_provider_list()
        for isp in isp_list:
            if self.country == isp['Country'] and self.city == isp['City'] \
               and self.name == isp['ProviderName']:
                return isp

    def setup_provider_db(self):
        self.dbtree.set_line_style(CTREE_LINES_DOTTED)
        self.dbtree.set_row_height(20)

        widget = self.xml.get_widget ('providerTree')

        pix_isp, mask_isp = GUI_functions.get_icon('isp.xpm')
        pix_city, mask_city = GUI_functions.get_icon('city.xpm')

        isp_list = self.get_provider_list()

        _country = ""
        _city = ""

        for isp in isp_list:
            if _country != isp['Country']:
                pix, mask = GUI_functions.get_icon(isp['Flag'] + '.xpm')
                if not pix:
                    pix, mask = GUI_functions.get_icon('unknown-flag.xpm' )

                country = self.dbtree.insert_node(None, None, 
                                                  [isp['Country']], 5, 
                                                  pix, mask, pix, mask, 
                                                  is_leaf=False)
                _country = isp['Country']
                _city = ''
                
            if _city != isp['City']:
                city = self.dbtree.insert_node(country, None, [isp['City']], 5, 
                                               pix_city, mask_city, 
                                               pix_city, mask_city, 
                                               is_leaf=False)
                _city = isp['City']
                
            self.dbtree.insert_node(city, None, 
                                    [isp['ProviderName']], 5, 
                                    pix_isp, mask_isp, 
                                    pix_isp, mask_isp, is_leaf=False)

        self.dbtree.select_row(0, 0)

    def on_tonlineButton_clicked(self, *args): # pylint: disable-msg=W0613
        self.dehydrate()
        dialup = self.device.createDialup() 
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
        self.xml.get_widget("dialupLoginNameEntry").set_text(dialup.Login)
        self.xml.get_widget("dialupPasswordEntry").set_text(dialup.Password)
        if not self.xml.get_widget("providerName").get_text():
            self.xml.get_widget("providerName").set_text("T-Online")

    def dehydrate(self):
        DeviceId = self.xml.get_widget('providerName').get_text()
        DeviceId = re.sub('-', '_', DeviceId)
        n = DeviceId
        num = 0
        while 1:
            found = 0
            for l in self.devicelist:
                if l.DeviceId == DeviceId:
                    found = 1
            if found != 1:
                break
            DeviceId = n + str(num)
            num = num + 1

        self.device.DeviceId = DeviceId
        self.device.Type = self.connection_type
        dialup = self.device.createDialup()
        self.device.AllowUser = True
        self.device.OnBoot = False
        dialup.Prefix = self.xml.get_widget('prefixEntry').get_text()
        dialup.Areacode = self.xml.get_widget('areaCodeEntry').get_text()
        dialup.PhoneNumber = self.xml.get_widget('phoneEntry').get_text()
        dialup.ProviderName = self.xml.get_widget('providerName').get_text()
        dialup.Login = self.xml.get_widget('dialupLoginNameEntry').get_text()
        dialup.Password = self.xml.get_widget('dialupPasswordEntry').get_text()
        if self.provider and self.provider['Authentication']:
            dialup.Authentication = self.provider['Authentication']
        else:
            dialup.Authentication = '+pap -chap'
        dialup.DefRoute = True
        dialup.DialMode = NCDialup.DM_MANUAL

        if self.connection_type == ISDN:
            dialup.HangupTimeout = 600
            dialup.EncapMode = 'syncppp'

        elif self.connection_type == MODEM:
            dialup.Inherits = 'Modem0'
            dialup.StupidMode = True
            dialup.InitString = ''
__author__ = "Harald Hoyer <harald@redhat.com>"
