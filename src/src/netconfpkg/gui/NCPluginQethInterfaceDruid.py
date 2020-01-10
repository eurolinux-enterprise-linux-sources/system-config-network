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
from netconfpkg import NCProfileList
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NCDeviceList import getDeviceList
from netconfpkg.NCHardwareList import getHardwareList
from netconfpkg.NC_functions import _, QETH, PROGNAME, NETCONFDIR
from netconfpkg.gui import sharedtcpip
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect, GLADEPATH
from netconfpkg.gui.InterfaceCreator import InterfaceCreator
from netconfpkg.gui.NCPluginQethHardwareDruid import QethHardware
from netconfpkg.plugins import NCPluginDevQeth
import ethtool

class QethInterfaceGui(InterfaceCreator):
    def __init__(self, toplevel=None, connection_type=QETH, do_save = 1,
                 druid = None):
        InterfaceCreator.__init__(self, do_save = do_save)
        self.toplevel = toplevel
        self.topdruid = druid
        self.connection_type = connection_type
        self.xml = None
        self.devlist = []

    def init_gui(self):
        # pylint: disable-msg=W0201
        if self.xml:
            return
        
        glade_file = "sharedtcpip.glade"
        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file
            
        self.sharedtcpip_xml = gtk.glade.XML (glade_file, None,
                                                  domain=PROGNAME)

        glade_file = 'QethInterfaceDruid.glade'

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
              "on_hw_config_page_back" : self.on_hw_config_page_back,
              "on_hw_config_page_next" : self.on_hw_config_page_next,
              "on_hw_config_page_prepare" : self.on_hw_config_page_prepare,
              "on_finish_page_finish" : self.on_finish_page_finish,
              "on_finish_page_prepare" : self.on_finish_page_prepare,
              "on_finish_page_back" : self.on_finish_page_back
              }
            )

        #print "EthernetInterface getDeviceList"
        self.devicelist = getDeviceList()
        df = getDeviceFactory()
        devclass = df.getDeviceClass(self.connection_type)
        if devclass:
            self.device = devclass()
        else:
            self.device = NCPluginDevQeth.DevQeth()
            
        self.device.Type = self.connection_type
        self.device.OnBoot = True
        self.device.AllowUser = False
        self.device.IPv6Init = False
        self.profilelist = NCProfileList.getProfileList()

        self.hw_sel = 0
        self.hwPage = False

        window = self.sharedtcpip_xml.get_widget ('dhcpWindow')
        frame = self.sharedtcpip_xml.get_widget ('dhcpFrame')
        vbox = self.xml.get_widget ('generalVbox')
        window.remove (frame)
        vbox.pack_start (frame)
        sharedtcpip.dhcp_init (self.sharedtcpip_xml, self.device)

        self.druids = []
        self.druid = self.xml.get_widget('druid')
        for i in self.druid.get_children():
            self.druid.remove(i)
            self.druids.append(i)

        if self.connection_type == QETH:
            self.hwDruid = QethHardware(self.toplevel)
            self.hwDruid.has_ethernet = None
            self.druids = [self.druids[0]] + self.hwDruid.druids[:]\
                          + self.druids[1:]

    def get_project_name(self):
        return _('Qeth connection')

    def get_type(self):
        return QETH
 
    def get_project_description(self):
        return _("Create a new qeth connection.")

    def get_druids(self):
        self.init_gui()
        return self.druids
    
    def on_hostname_config_page_back(self, 
                                druid_page, druid): # pylint: disable-msg=W0613
        childs = self.topdruid.get_children()
        if self.hwPage:
            self.topdruid.set_page(childs[len(self.hwDruid.druids)+1])
        else:
            self.topdruid.set_page(childs[1])            
        return True
    
    def on_hostname_config_page_next(self, 
                                druid_page, druid): # pylint: disable-msg=W0613
        sharedtcpip.dhcp_dehydrate (self.sharedtcpip_xml, self.device)
        if self.hwPage:
            self.device.Device = self.hwDruid.hw.Name
            self.device.Alias = None
        #self.device.Hostname = self.xml.get_widget("hostnameEntry").get_text()
    
    def on_hostname_config_page_prepare(self, 
                                druid_page, druid): # pylint: disable-msg=W0613
        self.device.DeviceId = self.device.Device
        if self.device.Alias:
            self.device.DeviceId = self.device.DeviceId + ":" \
                                   + str(self.device.Alias)
        sharedtcpip.dhcp_hydrate (self.sharedtcpip_xml, self.device)
    
    def on_hw_config_page_back(self, druid_page, druid):
        pass
    
    def on_hw_config_page_next(self, 
                               druid_page, druid): # pylint: disable-msg=W0613
        clist = self.xml.get_widget("hardwareList")
        childs = self.topdruid.get_children()

        if not len(clist.selection):
            self.topdruid.set_page(childs[1])
            return True

        self.hw_sel = clist.selection[0]
        
        if (self.hw_sel + 1) == clist.rows:
            self.hwPage = True
            self.topdruid.set_page(childs[len(self.hwDruid.druids)+1])
        else:
            self.hwPage = False
            self.device.Device = self.devlist[clist.selection[0]]
            
            self.device.Alias = self.getNextAlias(self.device)
            # must be at bottom, because prepare is called here
            self.topdruid.set_page(childs[len(self.hwDruid.druids)+2])

        return True

    def on_hw_config_page_prepare(self, 
                                druid_page, druid): # pylint: disable-msg=W0613
        hardwarelist = getHardwareList()
        hardwarelist.updateFromSystem()

        clist = self.xml.get_widget("hardwareList")
        clist.clear()
        self.devlist = []
        for hw in hardwarelist:
            if hw.Type == QETH:
                desc = hw.Description + " (" + hw.Name + ")"
                clist.append([desc])
                self.devlist.append(hw.Name)
                
        clist.append([_("Other QETH Device")])
        clist.select_row (self.hw_sel, 0)
    
    def on_finish_page_back(self, druid_page, druid):
        pass
        
    def on_finish_page_prepare(self, 
                               druid_page, druid): # pylint: disable-msg=W0613
        self.device.DeviceId = self.device.Device
        if self.device.Alias:
            self.device.DeviceId = self.device.DeviceId + ":" \
                                   + str(self.device.Alias)

        try: 
            hwaddr = ethtool.get_hwaddr(self.device.Device)
        except IOError:
            pass
        else:
            self.device.HardwareAddress = hwaddr

        # FIXME: Bad style for translation
        s = str(_("You have selected the following information:") 
                + "\n\n" + "   " + _("Device:") + " " 
                + str(self.device.DeviceId) + " ")

        hardwarelist = getHardwareList()
        for hw in hardwarelist:
            if hw.Name == self.device.Device:
                s = s + "(" + hw.Description + ")"
                break

        s = s + "\n" + "   "
        
        if (self.device.BootProto == "static" 
            or self.device.BootProto == "none"):
            s = str(s + _("Address:") + " " + self.device.IP + "\n" 
                    + "   " + _("Subnet mask:") + " " 
                    + self.device.Netmask + "\n" + "   "
                    + _("Default gateway address:") + " " 
                    + self.device.Gateway + "\n" + "   ")
        else:
            s = str(s + _("Automatically obtain IP address settings with:") 
                    + " " + self.device.BootProto + "\n")


        druid_page.set_text(s)
        
    def on_finish_page_finish(self, 
                              druid_page, druid): # pylint: disable-msg=W0613
        
        
        hardwarelist = getHardwareList()
        hardwarelist.commit() 
        #print self.devicelist
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
    NCPluginDevQeth.setDevQethWizard(QethInterfaceGui)
    
__author__ = "Harald Hoyer <harald@redhat.com>"
