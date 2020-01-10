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
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect


class editAdressDialog:
    def __init__(self, route=None):
        self.route = route

        glade_file = "editadress.glade"

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, 
                                 domain=GUI_functions.PROGNAME)

        xml_signal_autoconnect(self.xml,
            {
            "on_addressEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[a-f:0-9\.]"),
            "on_netmaskEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[a-f:0-9\.]"),
            "on_gatewayEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[a-f:0-9\.]"),
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked
            })

        self.xml.get_widget("addressPixmap").set_from_file(
                                GUI_functions.NETCONFDIR+"pixmaps/network.xpm")
        self.dialog = self.xml.get_widget("Dialog")
        #self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        #self.dialog.connect("hide", gtk.main_quit)

        self.hydrate()

    def on_Dialog_delete_event(self, *args):
        pass

    def on_okButton_clicked(self, button): # pylint: disable-msg=W0613
        self.dehydrate()

    def on_cancelButton_clicked(self, button):
        pass

    def on_generic_entry_insert_text(self, 
                    entry, partial_text, length, # pylint: disable-msg=W0613
                    pos, mstr):
        text = partial_text[0:length]
        if re.match(mstr, text):
            return
        entry.emit_stop_by_name('insert_text')

    def hydrate(self):
        if self.route.Address:
            self.xml.get_widget('addressEntry').set_text(self.route.Address)
        if self.route.Netmask:
            self.xml.get_widget('netmaskEntry').set_text(self.route.Netmask)
        if self.route.Gateway:
            self.xml.get_widget('gatewayEntry').set_text(self.route.Gateway)

    def dehydrate(self):
        # FIXME: [183337] system-config-network doesn't check route fields
        self.route.Address = self.xml.get_widget(
                                'addressEntry').get_text().strip()
        self.route.Netmask = self.xml.get_widget(
                                'netmaskEntry').get_text().strip()
        self.route.Gateway = self.xml.get_widget(
                                'gatewayEntry').get_text().strip()

__author__ = "Harald Hoyer <harald@redhat.com>"
