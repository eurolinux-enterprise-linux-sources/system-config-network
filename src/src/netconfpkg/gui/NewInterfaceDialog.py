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
from netconfpkg import NCHardwareList, NCDeviceList
from netconfpkg.NCDeviceFactory import getDeviceFactory
from netconfpkg.NC_functions import NETCONFDIR
from netconfpkg.gui import GUI_functions
from netconfpkg.gui.GUI_functions import load_icon, xml_signal_autoconnect


# do not remove this (needed to access methods of self.druid


class NewInterfaceDialog:
    def __init__(self, parent_dialog = None):
        self.creator = None
        glade_file = 'NewInterfaceDruid.glade'

        if not os.path.isfile(glade_file):
            glade_file = GUI_functions.GLADEPATH + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML (glade_file, 'toplevel',
                                  domain=GUI_functions.PROGNAME)

        # get the widgets we need
        self.toplevel = self.xml.get_widget ('toplevel')
        self.druid = self.xml.get_widget ('druid')
        self.start_page = self.xml.get_widget('start_page')
        self.interface_clist = self.xml.get_widget ('interface_clist')
        self.description_label = self.xml.get_widget ('description_label')

        if parent_dialog:
            self.toplevel.set_transient_for(parent_dialog)
            self.toplevel.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        else:
            self.toplevel.set_position (gtk.WIN_POS_CENTER)

        xml_signal_autoconnect (self.xml,
            { 'on_toplevel_delete_event' : self.on_cancel_interface,
              'on_druid_cancel' : self.on_cancel_interface,
              'on_start_page_prepare' : self.on_start_page_prepare,
              'on_start_page_next' : self.on_start_page_next,
              'on_interface_clist_select_row' : \
              self.on_interface_clist_select_row,
              })

        load_icon("network.xpm", self.toplevel)

        # Initialize the clist
        self.interface_clist.column_titles_passive ()
        self.interface_clist.set_row_height(20)

        self.interface_clist.clear()
        interfaces = []
        df = getDeviceFactory()
        dfk = df.keys()
        dfk.sort()
        for mtype in dfk:
            i = df.getDeviceClass(mtype)().getWizard()
            if i:
                interfaces.append(i)

        for iface_creator in interfaces:
            iface = iface_creator (self.toplevel, do_save = None,
                                   druid = self.druid)
            iftype = iface.get_type()
            row = self.interface_clist.append ( \
                [ iface.get_project_name () ] )

            device_pixmap, device_mask = \
                           GUI_functions.get_device_icon_mask(iftype,
                                                              self.toplevel)

            self.interface_clist.set_pixtext (row, 0,
                                              iface.get_project_name (), 5,
                                              device_pixmap, device_mask)

            self.interface_clist.set_row_data (row, iface)

        self.canceled = False

        self.interface_clist.select_row (0, 0)

        self.toplevel.show_all ()
        self.on_start_page_prepare (None, None)

    def on_start_page_prepare (self, 
                               druid_page, druid): # pylint: disable-msg=W0613
        self.interface_clist.grab_focus ()
        self.druid.set_buttons_sensitive (False, True, True, True)

    def on_start_page_next (self, 
                            druid, druid_page): # pylint: disable-msg=W0613
        interface = self.interface_clist.get_row_data (\
            self.interface_clist.selection[0])

        # remove all other children
        for i in self.druid.get_children()[1:]:
            self.druid.remove(i)

        druid_pages = interface.get_druids()
        if druid_pages:
            for i in druid_pages:
                self.druid.append_page(i)
                i.show()
            return False
        else:
            return True

    def on_cancel_interface(self, *args): # pylint: disable-msg=W0613
        hardwarelist = NCHardwareList.getHardwareList()
        hardwarelist.rollback() 
        devicelist = NCDeviceList.getDeviceList()
        devicelist.rollback()   
        self.toplevel.destroy()
        self.canceled = True
        gtk.main_quit()

    def on_interface_clist_select_row (self, clist, 
                                row, column, event): # pylint: disable-msg=W0613
        interface = self.interface_clist.get_row_data (row)
        if interface == None:
            return
        #self.description_label.set_text (interface.get_project_description ())

        buf = self.description_label.get_buffer()
        buf.set_text(interface.get_project_description ())

__author__ = "Harald Hoyer <harald@redhat.com>"
