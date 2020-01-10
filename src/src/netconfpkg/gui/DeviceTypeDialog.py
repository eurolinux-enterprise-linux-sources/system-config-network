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
from netconfpkg.NC_functions import (NETCONFDIR, PROGNAME, deviceTypes,
                                     MODEM, ISDN, ETHERNET, DSL, 
                                     TOKENRING, WIRELESS, LO)
from netconfpkg.gui.GUI_functions import (GLADEPATH, load_icon,
                                          xml_signal_autoconnect)


class DeviceTypeDialog:
    def __init__(self, device):
        self.device = device
        glade_file = "DeviceTypeDialog.glade"

        if not os.path.exists(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, domain=PROGNAME)
        xml_signal_autoconnect(self.xml, 
            {
            "on_okButton_clicked" : self.on_okButton_clicked, 
            "on_cancelButton_clicked" : self.on_cancelButton_clicked, 
            })

        self.dialog = self.xml.get_widget("Dialog")
        load_icon("network.xpm", self.dialog)

        devicetypes = deviceTypes[:]
        devicetypes.remove(LO)

        hardwarelist = NCHardwareList.getHardwareList()
        machine = os.uname()[4]
        ethernetFound = False
        modemFound = False
        isdnFound = False
        tokenringFound = False
        adslFound = False
        wirelessFound = False
        for hw in hardwarelist:
            if hw.Type == MODEM: 
                modemFound = True
            elif hw.Type == ISDN: 
                isdnFound = True
            elif hw.Type == ETHERNET:
                ethernetFound = True
                adslFound = True
                wirelessFound = True
            elif hw.Type == TOKENRING: tokenringFound = True
        if machine == 's390' or machine == 's390x':
            modemFound = False
            isdnFound = False
            adslFound = False
            wirelessFound = False
        if not modemFound: 
            devicetypes.remove(MODEM)
        if not isdnFound: 
            devicetypes.remove(ISDN)
        if not ethernetFound: 
            devicetypes.remove(ETHERNET)
        if not adslFound: 
            devicetypes.remove(DSL)
        if not tokenringFound: 
            devicetypes.remove(TOKENRING)
        if not wirelessFound: 
            devicetypes.remove(WIRELESS)

        omenu = self.xml.get_widget('deviceTypeOption')
        omenu.remove_menu ()
        menu = gtk.Menu ()
        for device_name in devicetypes:
            menu_item = gtk.MenuItem (device_name)
            menu_item.set_data ("device", device_name)
            menu_item.show ()
            menu.append (menu_item)
        menu.show ()
        omenu.set_menu (menu)
        omenu.grab_focus ()
        self.hydrate()


    def hydrate(self):
        pass

    def dehydrate(self):
        omenu = self.xml.get_widget('deviceTypeOption')
        item = omenu.get_menu ().get_active ()
        self.device.Type = item.get_data ("device")

    def on_okButton_clicked(self, button): # pylint: disable-msg=W0613
        self.dehydrate()

    def on_cancelButton_clicked(self, button): # pylint: disable-msg=W0613
        self.device.rollback()

__author__ = "Harald Hoyer <harald@redhat.com>"
