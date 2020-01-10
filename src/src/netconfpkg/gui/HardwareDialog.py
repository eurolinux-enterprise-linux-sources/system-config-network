## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>

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
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import load_icon, xml_signal_autoconnect


class HardwareDialog:
    def __init__(self, hw, glade_file, signals = None,
                 dialogname = "Dialog"):
        self.hw = hw

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, 
                                 domain=GUI_functions.PROGNAME)
        if signals:
            xml_signal_autoconnect(self.xml, signals)

        self.dialog = self.xml.get_widget(dialogname)
        self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        load_icon("network.xpm", self.dialog)

        self.setup()
        self.hydrate()

    def getDialog(self):
        return self.dialog

    def on_Dialog_delete_event(self, *args):
        pass

    def on_okButton_clicked(self, button): # pylint: disable-msg=W0613
        self.dehydrate()

    def on_cancelButton_clicked(self, button):
        pass

    def hydrate(self):
        pass

    def setup(self):
        pass

    def dehydrate(self):
        pass

__author__ = "Harald Hoyer <harald@redhat.com>"
