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
import re
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import xml_signal_autoconnect


class TonlineDialog:
    def __init__(self, login, pw):
        self.login = login
        self.password = pw

        glade_file = "tonline.glade"

        if not os.path.exists(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.exists(glade_file):
            glade_file = GUI_functions.NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, 
                                 domain=GUI_functions.PROGNAME)

        xml_signal_autoconnect(self.xml,
            {
            "on_AKEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[0-9]"),
            "on_ZNEntry_insert_text" : (self.on_generic_entry_insert_text,
                                             r"^[0-9]"),
            "on_mbnEntry_insert_text" : \
            (self.on_generic_entry_insert_text, r"^[0-9]"),
            "on_AKEntry_changed" : (self.on_generic_entry_changed, 1),
            "on_ZNEntry_changed" : (self.on_generic_entry_changed, 1),
            "on_mbnEntry_changed" : (self.on_generic_entry_changed, 1),
            "on_pwEntry_changed" : (self.on_generic_entry_changed, 1),
            "on_okButton_clicked" : self.on_okButton_clicked,
            "on_cancelButton_clicked" : self.on_cancelButton_clicked
            })

        self.dialog = self.xml.get_widget("Dialog")

        self.hydrate()

    def on_okButton_clicked(self, button): # pylint: disable-msg=W0613
        self.dehydrate()

    def on_cancelButton_clicked(self, button):
        pass

    def check(self):
        if (len(self.xml.get_widget('AKEntry').get_text()) < 1 or 
           len(self.xml.get_widget('ZNEntry').get_text()) < 1 or 
           len(self.xml.get_widget('mbnEntry').get_text()) < 1 or
           len(self.xml.get_widget('pwEntry').get_text()) < 1 ):
            self.xml.get_widget('okButton').set_sensitive(False)
        else:
            self.xml.get_widget('okButton').set_sensitive(True)

    def on_generic_entry_insert_text(self, 
                        entry, partial_text, length, # pylint: disable-msg=W0613
                        pos, mstr):
        text = partial_text[0:length]

        if re.match(mstr, text):
            return
        entry.emit_stop_by_name('insert_text')

    def on_generic_entry_changed(self, entry, minlen):
        if len(entry.get_text()) < minlen:
            self.xml.get_widget('okButton').set_sensitive(False)
        self.check()

    def hydrate(self):
        ak = ""
        zn = ""
        mbn = ""
        if self.login:
            s = self.login.split("@")[0]
            s2 = s.split("#")
            if len(s2) > 1:
                mbn = s2[1]

            s = s2[0]
            if s > 12:
                ak = s[:12]
                zn = s[12:]
            else:
                ak = s

        self.xml.get_widget('AKEntry').set_text(ak)
        self.xml.get_widget('ZNEntry').set_text(zn)
        self.xml.get_widget('mbnEntry').set_text(mbn)
        self.xml.get_widget('pwEntry').set_text(self.password)
        self.check()

    def dehydrate(self):
        self.login = "%s%s#%s@t-online.de" % \
                     (self.xml.get_widget('AKEntry').get_text(),
                      self.xml.get_widget('ZNEntry').get_text(),
                      self.xml.get_widget('mbnEntry').get_text())

        self.password = self.xml.get_widget('pwEntry').get_text()

__author__ = "Harald Hoyer <harald@redhat.com>"
