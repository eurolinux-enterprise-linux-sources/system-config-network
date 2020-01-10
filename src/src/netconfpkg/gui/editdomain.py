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
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import load_icon, xml_signal_autoconnect


class editDomainDialog:
    def __init__(self, Name):
        self.Name = Name

        glade_file = "editdomain.glade"

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, 
                                 domain=GUI_functions.PROGNAME)

        xml_signal_autoconnect(self.xml,
            {
            "on_domainNameEntry_insert_text" : 
                (self.on_domainNameEntry_insert_text, ""),
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked
            })

        self.dialog = self.xml.get_widget("Dialog")
        #self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        #self.dialog.connect("hide", gtk.main_quit)

        load_icon("network.xpm", self.dialog)
        self.setup()
        self.hydrate()

    def on_Dialog_delete_event(self, *args):
        pass
    #    self.dialog.destroy()

    def on_okButton_clicked(self, button): # pylint: disable-msg=W0613
        self.dehydrate()
    #    self.main.hydrate()
    #    self.dialog.destroy()

    def on_cancelButton_clicked(self, button):
        pass
    #    self.dialog.destroy()

    def on_domainNameEntry_insert_text(self, 
                        entry, partial_text, length, # pylint: disable-msg=W0613
                        pos, mstr): 
        pass

    def hydrate(self):
        pass

    def dehydrate(self):
        profilelist = NCProfileList.getProfileList()

        for prof in profilelist:
            if prof.Active == True:
                index = prof.DNS.SearchList.index(self.Name)
                n = self.xml.get_widget("domainNameEntry").get_text()

                if len(n.strip()) == 0:
                    del prof.DNS.SearchList[index]
                else:
                    prof.DNS.SearchList[index] = n

                self.hydrate()
                prof.DNS.SearchList.commit()

    def setup(self):
        self.xml.get_widget("domainNameEntry").set_text(self.Name)



__author__ = "Harald Hoyer <harald@redhat.com>"
