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
from netconfpkg.NCHardwareFactory import getHardwareFactory
from netconfpkg.NC_functions import (NETCONFDIR, PROGNAME, ETHERNET, 
                                     TOKENRING, ISDN)
from netconfpkg.gui.GUI_functions import (GLADEPATH, load_icon,
                                          xml_signal_autoconnect)


class hardwareTypeDialog:
    def __init__(self):
        glade_file = "hardwaretype.glade"

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
        self.Type = None
        machine = os.uname()[4]
        hardwarelist = NCHardwareList.getHardwareList()
        if machine == 's390' or machine == 's390x':
            devicetypes = [ ETHERNET, TOKENRING, QETH ]
        else:
            df = getHardwareFactory()
            devicetypes = df.keys()

        for hw in hardwarelist:
            if hw.Type == ISDN:
                devicetypes.remove(ISDN)
                break


        self.xml.get_widget(
            'hardwareTypeCombo').set_popdown_strings(devicetypes)
        self.hydrate()

    def hydrate(self):
        pass

    def dehydrate(self):
        self.Type = self.xml.get_widget('hardwareTypeEntry').get_text()

    def on_okButton_clicked(self, button): # pylint: disable-msg=W0613
        self.dehydrate()

    def on_cancelButton_clicked(self, button):
        pass

__author__ = "Harald Hoyer <harald@redhat.com>"
