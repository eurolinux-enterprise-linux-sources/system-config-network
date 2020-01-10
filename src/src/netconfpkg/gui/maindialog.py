# -*- coding: utf-8 -*-
## Copyright (C) 2001-2006 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>
## Copyright (C) 2001, 2002 Trond Eivind Glomsrød <teg@redhat.com>
## Copyright (C) 2001-2006 Harald Hoyer <harald@redhat.com>

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
"""
netconf - A network configuration tool

The GUI maindialog of s-c-network
"""


#import gnome # pylint: disable-msg=W0611
import gnome.ui # needed before the glade xml load
import gobject
import gtk.glade
import os
import re
from netconfpkg import NCDeviceFactory
from netconfpkg.Control import NetworkDevice
from netconfpkg.NCDeviceList import getDeviceList
from netconfpkg.NCHardwareList import getHardwareList
from netconfpkg.NCHost import Host
from netconfpkg.NCIPsec import IPsec
from netconfpkg.NCIPsecList import getIPsecList
from netconfpkg.NCProfileList import getProfileList, Profile
from netconfpkg.NCRoute import testIP
from netconfpkg.NC_functions import (DEFAULT_PROFILE_NAME, PROGNAME,
                                     rpms_notinstalled, log, NETCONFDIR, 
                                     LO, TestError, _, 
                                     generic_error_dialog,
                                     generic_yesno_dialog, 
                                     ACTIVE, INACTIVE, 
                                     generic_yesnocancel_dialog, 
                                     generic_info_dialog, 
                                     )
from netconfpkg.gui.GUI_functions import (get_icon, get_pixbuf,
                                          GLADEPATH, load_icon, 
                                          xml_signal_autoconnect,
                                          get_device_icon_mask, 
                                          gui_info_dialog,
                                          RESPONSE_YES, RESPONSE_NO,
                                          RESPONSE_CANCEL,
                                          gui_run,
                                          on_generic_clist_button_release_event,
                                          on_generic_entry_insert_text,
                                          )
from netconfpkg.gui.NewInterfaceDialog import NewInterfaceDialog
from netconfpkg.gui.edithosts import editHostsDialog


PROFILE_COLUMN = 0
STATUS_COLUMN = 1
DEVICE_COLUMN = 2
NICKNAME_COLUMN = 3
TYPE_COLUMN = 4

PAGE_DEVICES = 0
PAGE_HARDWARE = 1
PAGE_IPSEC = 2
PAGE_DNS = 3
PAGE_HOSTS = 4

def _nop(*args, **kwargs): # pylint: disable-msg=W0613
    pass

class mainDialog:
    # pylint: disable-msg=W0201
    def __init__(self):
        glade_file = "maindialog.glade"

        if not os.path.isfile(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.xml = gtk.glade.XML(glade_file, None, domain=PROGNAME)
        self.initialized = None
        self.help_displayed = False
        self.no_profileentry_update = None
        self.ignore_widget_changes = True

        self.edit_button = self.xml.get_widget("editButton")
        self.delete_button = self.xml.get_widget("deleteButton")
        self.copy_button = self.xml.get_widget("copyButton")
        self.activate_button = self.xml.get_widget("activateButton")
        self.deactivate_button = self.xml.get_widget("deactivateButton")
        self.up_button = self.xml.get_widget("upButton")
        self.down_button = self.xml.get_widget("downButton")

        xml_signal_autoconnect(self.xml,
            {
            "on_activateButton_clicked" : \
            self.on_activateButton_clicked,
            "on_deactivateButton_clicked" : \
            self.on_deactivateButton_clicked,
            "on_deviceList_select_row" :
            self.on_generic_clist_select_row,
            "on_deviceList_unselect_row" :
            self.on_generic_clist_unselect_row,
            "on_deviceList_button_press_event" : \
            self.on_generic_clist_button_press_event,
            "on_save_activate" : self.on_applyButton_clicked,
            "on_quit_activate" : self.on_okButton_clicked,
            "on_contents_activate" : self.on_helpButton_clicked,
            "on_hardwareList_select_row" :
            self.on_generic_clist_select_row,
            "on_hardwareList_unselect_row" :
            self.on_generic_clist_unselect_row,
            "on_hardwareList_button_press_event" : \
            self.on_generic_clist_button_press_event,
            "on_ipsecList_button_press_event" : \
            self.on_generic_clist_button_press_event,            
            "on_hostnameEntry_changed" : self.on_hostnameEntry_changed,
            "on_domainEntry_changed" : self.on_domainEntry_changed,
            "on_primaryDnsEntry_changed" : self.on_primaryDnsEntry_changed,
            "on_secondaryDnsEntry_changed" : 
                self.on_secondaryDnsEntry_changed,
            "on_tertiaryDnsEntry_changed" : 
                self.on_tertiaryDnsEntry_changed,
            "on_searchDnsEntry_changed" : self.on_searchDnsEntry_changed,
            "on_profileAddMenu_activate" : self.on_profileAddMenu_activate,
            "on_profileCopyMenu_activate" : self.on_profileCopyMenu_activate,
            "on_profileRenameMenu_activate": \
            self.on_profileRenameMenu_activate,
            "on_profileDeleteMenu_activate" : \
            self.on_profileDeleteMenu_activate,
            "on_ProfileNameEntry_insert_text" : ( \
            on_generic_entry_insert_text, r"^[a-z|A-Z|0-9]+$"),
            "on_about_activate" : self.on_about_activate,
            "on_mainNotebook_switch_page" : self.on_mainNotebook_switch_page,
            "on_addButton_clicked" : self.on_addButton_clicked,
            "on_editButton_clicked" : self.on_editButton_clicked,
            "on_deleteButton_clicked" : self.on_deleteButton_clicked,
            "on_copyButton_clicked" : self.on_copyButton_clicked,
            "on_upButton_clicked" : self.on_upButton_clicked,
            "on_downButton_clicked" : self.on_downButton_clicked,
            "on_show_loopback_toggled" : self.on_show_loopback_toggled,
        })

        self.appBar = self.xml.get_widget ("appbar")
        if not hasattr(self.appBar, "push") or not hasattr(self.appBar, "push"):
            self.appBar.push = _nop
            self.appBar.pop = _nop

        # FIXME: [188232] 'NoneType' object has no attribute 'set_from_pixbuf'
        widget = self.xml.get_widget ("hardware_pixmap")
        widget.set_from_pixbuf(get_pixbuf("connection-ethernet.png"))
        widget = self.xml.get_widget ("hosts_pixmap")
        widget.set_from_pixbuf(get_pixbuf("nameresolution_alias.png"))
        widget = self.xml.get_widget ("dns_pixmap")
        widget.set_from_pixbuf(get_pixbuf("nameresolution_alias.png"))
        widget = self.xml.get_widget ("devices_pixmap")
        widget.set_from_pixbuf(get_pixbuf("network.png"))
        widget = self.xml.get_widget ("ipsec_pixmap")
        widget.set_from_pixbuf(get_pixbuf("secure.png"))

        self.dialog = self.xml.get_widget("Dialog")
        self.dialog.set_position (gtk.WIN_POS_CENTER)
        self.dialog.connect("delete-event", self.on_Dialog_delete_event)
        self.dialog.connect("hide", gtk.main_quit)

        self.xml.get_widget ("profileMenu").show()

        self.on_xpm, self.on_mask = get_icon('on.xpm')
        self.off_xpm, self.off_mask = get_icon('off.xpm')
        self.act_xpm, self.act_mask = get_icon ("active.xpm")
        self.inact_xpm, self.inact_mask = get_icon ("inactive.xpm")
        self.devsel = None
        self.hwsel = None
        self.ipsel = None
        self.lastbuttonevent = None
        self.active_profile_name = DEFAULT_PROFILE_NAME

        load_icon("network.xpm", self.dialog)

        self.xml.get_widget ("deviceList").column_titles_passive ()
        self.xml.get_widget ("hardwareList").column_titles_passive ()
        #self.xml.get_widget ("hostsList").column_titles_passive ()

        notebook = self.xml.get_widget('mainNotebook')
        widget = self.xml.get_widget('deviceFrame')
        page = notebook.page_num(widget)
        notebook.set_current_page(page)

        if rpms_notinstalled(["ipsec-tools"]) == []:
            do_ipsec = True
        else:
            do_ipsec = False

        if not do_ipsec:
            # remove IPsec
            widget = self.xml.get_widget('ipsecFrame')
            page = notebook.page_num(widget)
            notebook.remove_page(page)

        self.page_num = {
            PAGE_DEVICES : notebook.page_num(\
            self.xml.get_widget('deviceFrame')),
            PAGE_HARDWARE : notebook.page_num(\
            self.xml.get_widget('hardwareFrame')),
            PAGE_IPSEC : -1,
            PAGE_HOSTS : notebook.page_num(\
            self.xml.get_widget('hostFrame')),
            PAGE_DNS : notebook.page_num(\
            self.xml.get_widget('dnsFrame')),
            }

        if do_ipsec:
            self.page_num[PAGE_IPSEC] = notebook.page_num(\
                self.xml.get_widget('ipsecFrame'))

        self.active_page = self.page_num[PAGE_DEVICES]

        self.addButtonFunc = {
            self.page_num[PAGE_DEVICES] : self.on_deviceAddButton_clicked,
            self.page_num[PAGE_HARDWARE] : self.on_hardwareAddButton_clicked,
            self.page_num[PAGE_IPSEC] : self.on_ipsecAddButton_clicked,
            self.page_num[PAGE_HOSTS] : self.on_hostsAddButton_clicked,
            }

        self.activateButtonFunc = {
            self.page_num[PAGE_DEVICES] : \
            self.on_deviceActivateButton_clicked,
            self.page_num[PAGE_HARDWARE] : self.nop,
            self.page_num[PAGE_IPSEC] : self.on_ipsecActivateButton_clicked,
            self.page_num[PAGE_HOSTS] : self.nop,
            }

        self.deactivateButtonFunc = {
            self.page_num[PAGE_DEVICES] : \
            self.on_deviceDeactivateButton_clicked,
            self.page_num[PAGE_HARDWARE] : self.nop,
            self.page_num[PAGE_IPSEC] : \
            self.on_ipsecDeactivateButton_clicked,
            self.page_num[PAGE_HOSTS] : self.nop,
            }

        self.editButtonFunc = {
            self.page_num[PAGE_DEVICES] : self.on_deviceEditButton_clicked,
            self.page_num[PAGE_HARDWARE] : \
            self.on_hardwareEditButton_clicked,
            self.page_num[PAGE_IPSEC] : self.on_ipsecEditButton_clicked,
            self.page_num[PAGE_HOSTS] : self.on_hostsEditButton_clicked,
            }

        self.copyButtonFunc = {
            self.page_num[PAGE_DEVICES] : self.on_deviceCopyButton_clicked,
            self.page_num[PAGE_HARDWARE] : self.nop,
            self.page_num[PAGE_IPSEC] : self.nop,
            self.page_num[PAGE_HOSTS] : self.nop,
            }

        self.deleteButtonFunc = {
            self.page_num[PAGE_DEVICES] : self.on_deviceDeleteButton_clicked,
            self.page_num[PAGE_HARDWARE] : \
            self.on_hardwareDeleteButton_clicked,
            self.page_num[PAGE_IPSEC] : self.on_ipsecDeleteButton_clicked,
            self.page_num[PAGE_HOSTS] : self.on_hostsDeleteButton_clicked,
            }

        self.editMap = {
            "deviceList" : PAGE_DEVICES,
            "hardwareList" : PAGE_HARDWARE,
            "ipsecList" : PAGE_IPSEC,
            }

        hclist = self.xml.get_widget("hostsList")
        # create the TreeViewColumns to display the data
        columns = [None]*3
        columns[0] = gtk.TreeViewColumn('IP')
        columns[1] = gtk.TreeViewColumn('Hostname')
        columns[2] = gtk.TreeViewColumn('Aliases')
        # create list
        self.hostsListStore = gtk.ListStore(str, str, str, object)
        # set filter
        self.modelfilter = self.hostsListStore.filter_new()
        self.modelfilter.set_visible_func(self.filter_loopback, None)
        hclist.set_model(self.modelfilter)
        for column in columns:
            n = hclist.append_column(column)
            column.cell = gtk.CellRendererText()
            column.pack_start(column.cell, False)
            column.set_attributes(column.cell, text=(n-1))
            column.set_resizable(True)
        self.modelfilter.refilter()
        hclist.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        self.load()
        self.hydrate()

        self.activedevicelist = NetworkDevice().get()
        self.tag = gobject.timeout_add(4000, self.updateDevicelist)

        # initialize the button state..
        clist = self.xml.get_widget("deviceList")
        self.on_generic_clist_select_row(\
            clist, 0, 0, 0)

        gtk.Tooltips().enable()

        self.dialog.show()

        self.on_mainNotebook_switch_page(None, None,
                                         self.page_num[PAGE_DEVICES])

        
    def nop(self, *args):
        pass

    def load(self):
        self.appBar.push(_("Loading configuration..."))
        self.loadDevices()
        self.loadHardware()
        self.loadProfiles()
        self.loadIPsec()
        self.appBar.pop()

    def loadDevices(self):
        self.appBar.push(_("Loading device configuration..."))
        devicelist = getDeviceList() # pylint: disable-msg=W0612
        self.appBar.pop()

    def loadHardware(self):
        self.appBar.push(_("Loading hardware configuration..."))
        hardwarelist = getHardwareList() # pylint: disable-msg=W0612
        self.appBar.pop()

    def loadProfiles(self):
        self.appBar.push(_("Loading profile configuration..."))
        profilelist = getProfileList()
        if profilelist.error:
            gui_info_dialog(profilelist.error, None)
        self.appBar.pop()

    def loadIPsec(self):
        self.appBar.push(_("Loading IPsec configuration..."))
        ipseclist = getIPsecList() # pylint: disable-msg=W0612
        self.appBar.pop()

    def test(self):
        self.appBar.push(_("Testing configuration set..."))
        profilelist = getProfileList()
        devicelist = getDeviceList()
        hardwarelist = getHardwareList()
        ipseclist = getIPsecList()
        try:
            hardwarelist.test()
            devicelist.test()
            profilelist.test()
            ipseclist.test()
        except TestError, msg:
            generic_error_dialog (str(msg), self.dialog)
            self.appBar.pop()
            return 1

        self.appBar.pop()
        return 0

    def ischanged(self):
        profilelist = getProfileList()
        devicelist = getDeviceList()
        hardwarelist = getHardwareList()
        ipseclist = getIPsecList()
        self.appBar.pop()

        profname = self.active_profile_name

        if profilelist.modified() \
               or devicelist.modified() \
               or hardwarelist.modified() \
               or ipseclist.modified():
            self.appBar.push(_("Active profile: %s (modified)") % \
                             self.active_profile_name)
            return True

        self.appBar.push(_("Active profile: %s")% profname)

        return False

    def save(self):
        try:
            self.test()
        except ValueError, e:
            retval = generic_yesno_dialog(
                "Errors detected, do you really want to save?\n" + e.message,
                self.dialog)
            if retval == gtk.RESPONSE_NO:
                return
                
        self.appBar.push(_("Saving configuration..."))
        self.appBar.refresh()
        profilelist = getProfileList()
        try:
            profilelist.fixInterfaces()
            self.saveHardware()
            self.saveDevices()
            self.saveIPsecs()
            self.saveProfiles()
            self.appBar.pop()
            self.checkApply()
        except (IOError, OSError, EnvironmentError, ValueError), errstr:
            generic_error_dialog (_("Error saving configuration!\n%s")
                                      % (str(errstr)))
        else:
            generic_info_dialog (_("Changes are saved. "
                                   "You may want to restart "
                                   "the network and network services "
                                   "or restart the computer."),
                                   self.dialog)
        self.appBar.pop()
        return 0

    def saveDevices(self):
        self.appBar.push(_("Saving device configuration..."))
        devicelist = getDeviceList()
        devicelist.save()
        devicelist.setunmodified()
        self.appBar.pop()

    def saveHardware(self):
        self.appBar.push(_("Saving hardware configuration..."))
        hardwarelist = getHardwareList()
        hardwarelist.save()
        hardwarelist.setunmodified()
        self.appBar.pop()

    def saveProfiles(self):
        self.appBar.push(_("Saving profile configuration..."))
        profilelist = getProfileList()
        active = profilelist.getActiveProfile() 
        if active is not None and active.DNS is not None:
            dns = profilelist.getActiveProfile().DNS.PrimaryDNS
            if dns and not testIP(dns):
                raise ValueError(_("Primary DNS is not in the correct format"))

            dns = profilelist.getActiveProfile().DNS.SecondaryDNS
            if dns and not testIP(dns):
                raise ValueError(_("Secondary DNS is not in the correct format"))

            dns = profilelist.getActiveProfile().DNS.TertiaryDNS
            if dns and not testIP(dns):
                raise ValueError(_("Tertiary DNS is not in the correct format"))

        profilelist.save()
        profilelist.setunmodified()
        self.appBar.pop()

    def saveIPsecs(self):
        self.appBar.push(_("Saving IPsec configuration..."))
        ipseclist = getIPsecList()
        ipseclist.save()
        ipseclist.setunmodified()
        self.appBar.pop()

    def hydrate(self):
        self.hydrateProfiles()
        self.hydrateDevices()
        self.hydrateHardware()
        self.hydrateIPsec()
        self.on_mainNotebook_switch_page(None, None,
                                         self.active_page)

    def checkApply(self, ch = -1):
        if ch == -1:
            ch = self.ischanged()

    def hydrateDevices(self):
        self.appBar.push(_("Updating devices..."))
        devicelist = getDeviceList()
        activedevicelist = NetworkDevice().get()
        profilelist = getProfileList()
        devsel = self.devsel

        clist = self.xml.get_widget("deviceList")

        clist.clear()

        clist.set_row_height(17)
        status_pixmap = self.off_xpm
        status_mask = self.off_mask
        status = INACTIVE

        row = 0
        for dev in devicelist:
            devname = dev.getDeviceAlias()

            if devname in activedevicelist:
                status = ACTIVE
                status_pixmap = self.on_xpm
                status_mask = self.on_mask
            else:
                status = INACTIVE
                status_pixmap = self.off_xpm
                status_mask = self.off_mask

            device_pixmap, device_mask = \
                get_device_icon_mask(dev.Type, self.dialog)

            clist.append(['', status, devname, dev.DeviceId, dev.Type])
            if self.inact_xpm:
                clist.set_pixmap(row, PROFILE_COLUMN, self.inact_xpm,
                                 self.inact_mask)
            if status_pixmap:
                clist.set_pixtext(row, STATUS_COLUMN, status, 5,
                                  status_pixmap, status_mask)

            if device_pixmap:
                clist.set_pixtext(row, DEVICE_COLUMN, devname, 5,
                                  device_pixmap, device_mask)

            clist.set_row_data(row, dev)

            for prof in profilelist:
                if ((prof.Active == True or prof.ProfileName == 'default')
                     and dev.DeviceId in prof.ActiveDevices):
                    if self.act_xpm:
                        clist.set_pixmap(row, PROFILE_COLUMN,
                                         self.act_xpm, self.act_mask)
                    break


            if dev == devsel or devsel == None:
                log.log(5, "Selecting row %d" % row)
                clist.select_row(row, 0)
                devsel = dev

            row = row + 1
        self.appBar.pop()
        self.checkApply()

    def hydrateHardware(self):
        self.appBar.push(_("Updating hardware..."))
        hardwarelist = getHardwareList()
        clist = self.xml.get_widget("hardwareList")
        clist.clear()
        clist.set_row_height(17)
        row = 0
        hwsel = self.hwsel

        for hw in hardwarelist:
            clist.append([str(hw.Description), str(hw.Type), 
                          str(hw.Name), _(str(hw.Status))])
            device_pixmap, device_mask = \
                get_device_icon_mask(hw.Type, self.dialog)
            if device_pixmap:
                clist.set_pixtext(row, DEVICE_COLUMN, hw.Name, 5,
                                  device_pixmap, device_mask)
            clist.set_row_data(row, hw)

            if hw == hwsel:
                log.log(5, "Selecting row %d" % row)
                clist.select_row(row, 0)

            row += 1
        self.appBar.pop()
        self.checkApply()

    def hydrateIPsec(self):
        ipseclist = getIPsecList()
        clist = self.xml.get_widget("ipsecList")
        if not clist:
            return
        clist.clear()
        clist.set_row_height(17)
        row = 0
        ipsel = self.ipsel
        profilelist = getProfileList()

        for ipsec in ipseclist:
            clist.append(['', str(ipsec.ConnectionType),
                          str(ipsec.RemoteIPAddress),
                          str(ipsec.IPsecId)])

            clist.set_pixmap(row, PROFILE_COLUMN, self.inact_xpm,
                             self.inact_mask)
            clist.set_row_data(row, ipsec)

            for prof in profilelist:
                if ((prof.Active == True or prof.ProfileName == 'default')
                     and ipsec.IPsecId in prof.ActiveIPsecs):
                    clist.set_pixmap(row, PROFILE_COLUMN,
                                     self.act_xpm, self.act_mask)
                    break


            if ipsec == ipsel:
                log.log(5, "Selecting row %d" % row)
                clist.select_row(row, 0)

            row += 1
        self.appBar.pop()
        self.checkApply()

    def getActiveProfile(self):
        return self.active_profile

    def filter_loopback(self, model, miter, data): # pylint: disable-msg=W0613
        if self.xml.get_widget("show_loopback").get_active():
            return True
        else:
            return model.get_value(miter, 0) not in ["127.0.0.1", "::1"]

    def on_show_loopback_toggled(self, *args): # pylint: disable-msg=W0613
        self.xml.get_widget("hostsList").get_model().refilter()
        
        
    def hydrateProfiles(self):
        self.appBar.push(_("Updating profiles..."))
        profilelist = getProfileList()

        for prof in profilelist:
            if not prof.Active:
                continue

            name = prof.ProfileName
            if name == "default":
                name = DEFAULT_PROFILE_NAME
            self.active_profile_name = name
            break
        else:
            prof = profilelist[0]

        # pylint: disable-msg=W0631
        self.active_profile = prof 
        self.ignore_widget_changes = True

        for key, widget in { "Hostname" : "hostnameEntry", 
                             "Domainname" : "domainnameEntry", 
                             "PrimaryDNS" : "primaryDnsEntry",
                             "SecondaryDNS" : "secondaryDnsEntry", 
                             "TertiaryDNS" : "tertiaryDnsEntry"
                             }.items():
            txt = getattr(prof.DNS, key)
            self.xml.get_widget(widget).set_text(txt or '')

        if prof.DNS.SearchList:
            self.xml.get_widget('searchDnsEntry').set_text(
                " ".join(prof.DNS.SearchList))
        else:
            self.xml.get_widget('searchDnsEntry').set_text('')

        self.ignore_widget_changes = False

        # clear the store
        self.hostsListStore.clear()
        # load hosts to list
        for host in prof.HostsList:
            if host.AliasList:
                self.hostsListStore.append([host.IP, host.Hostname,
                               " ".join(host.AliasList), host])
            else:
                self.hostsListStore.append([host.IP, host.Hostname, "", host])
            
        if self.initialized:
            self.appBar.pop()
            self.checkApply()
            return

        self.initialized = True

        self.no_profileentry_update = True
        self.ignore_widget_changes = False
        omenu = self.xml.get_widget('profileMenu')
        omenu = omenu.get_submenu()
        clist = omenu.get_children()
        for child in clist[5:]:
            omenu.remove(child)

        group = None
        for prof in profilelist:
            name = prof.ProfileName
            # change the default profile to a more understandable name
            if name == "default":
                name = DEFAULT_PROFILE_NAME
            menu_item = gtk.RadioMenuItem (group, label = name)
            if not group:
                group = menu_item
            menu_item.show ()
            if prof.Active:
                menu_item.set_active(True)
            menu_item.connect ("activate",
                               self.on_profileMenuItem_activated,
                               prof.ProfileName)
            omenu.append (menu_item)
        self.no_profileentry_update = False
        self.appBar.pop()
        self.checkApply()

    def updateDevicelist(self):
        activedevicelistold = self.activedevicelist
        self.activedevicelist = NetworkDevice().get()

        if activedevicelistold != self.activedevicelist:
            self.hydrateDevices()
            return True

        return True

    def on_Dialog_delete_event(self, *args): # pylint: disable-msg=W0613
        profilelist = getProfileList()
        try:
            profilelist.test()
        except:
            button = generic_yesno_dialog(
                _("Errors detected, do you really want to quit?"),
                self.dialog)
            if button == RESPONSE_NO:
                return True
        
        # no errors or user wants to save anyway...
        if self.ischanged():
            button = generic_yesnocancel_dialog(
                _("Do you want to save your changes?"),
                self.dialog)
            if button == RESPONSE_YES:
                try:
                    self.save()
                except:
                    pass
            if button == RESPONSE_CANCEL:
                return True

        gtk.main_quit()
        return

    def on_okButton_clicked (self, *args): # pylint: disable-msg=W0613
        profilelist = getProfileList()
        profilelist.commit()

        if self.ischanged():
            button = generic_yesnocancel_dialog(
                _("Do you want to save your changes?"),
                self.dialog)

            if button == RESPONSE_CANCEL:
                return

            if button == RESPONSE_YES:
                if self.save() != 0:
                    return

        gtk.main_quit()
        return

    def on_mainNotebook_switch_page(self, 
                                    page = None, 
                                    a = None, # pylint: disable-msg=W0613
                                    page_num = 0, 
                                    *args): # pylint: disable-msg=W0613
        self.active_page = page_num

        # Check if we aren't called in a dialog destroy event
        if self.xml.get_widget ("addButton") == None:
            return

        self.xml.get_widget ("addButton").set_sensitive(False)
        self.xml.get_widget ("editButton").set_sensitive(False)
        self.xml.get_widget ("copyButton").set_sensitive(False)
        self.xml.get_widget ("deleteButton").set_sensitive(False)
        self.xml.get_widget ("commonDockitem").hide()
        self.xml.get_widget ("deviceDockitem").hide()
        self.xml.get_widget ("posDockitem").hide()

        if page_num == self.page_num[PAGE_DEVICES]:
            clist = self.xml.get_widget("deviceList")
            self.xml.get_widget ("addButton").set_sensitive(True)
            self.xml.get_widget ("editButton").set_sensitive(True)
            self.xml.get_widget ("copyButton").set_sensitive(True)
            self.xml.get_widget ("deleteButton").set_sensitive(True)
            self.xml.get_widget ("commonDockitem").show()
            self.xml.get_widget ("deviceDockitem").show()

        elif page_num == self.page_num[PAGE_HARDWARE]:
            clist = self.xml.get_widget("hardwareList")
            self.xml.get_widget ("addButton").set_sensitive(True)
            self.xml.get_widget ("editButton").set_sensitive(True)
            self.xml.get_widget ("deleteButton").set_sensitive(True)
            self.xml.get_widget ("commonDockitem").show()

        elif page_num == self.page_num[PAGE_IPSEC]:
            clist = self.xml.get_widget("ipsecList")
            self.xml.get_widget ("addButton").set_sensitive(True)
            self.xml.get_widget ("editButton").set_sensitive(True)
            self.xml.get_widget ("deleteButton").set_sensitive(True)
            self.xml.get_widget ("commonDockitem").show()
            self.xml.get_widget ("deviceDockitem").show()

        elif page_num == self.page_num[PAGE_HOSTS]:
            clist = None
            self.xml.get_widget ("addButton").set_sensitive(True)
            self.xml.get_widget ("editButton").set_sensitive(True)
            self.xml.get_widget ("deleteButton").set_sensitive(True)
            self.xml.get_widget ("commonDockitem").show()

        elif page_num == self.page_num[PAGE_DNS]:
            clist = None
            self.xml.get_widget ("commonDockitem").show()

        if clist:
            self.on_generic_clist_select_row(clist, 0, 0, 0)


    def on_activateButton_clicked (self, button):
        self.activateButtonFunc[self.active_page](button)

    def on_deactivateButton_clicked (self, button):
        self.deactivateButtonFunc[self.active_page](button)

    def on_addButton_clicked (self, button):
        self.addButtonFunc[self.active_page](button)

    def on_editButton_clicked (self, button):
        self.editButtonFunc[self.active_page](button)

    def on_copyButton_clicked (self, button):
        self.copyButtonFunc[self.active_page](button)

    def on_deleteButton_clicked (self, button):
        self.deleteButtonFunc[self.active_page](button)

    def on_upButton_clicked (self, button):
        pass

    def on_downButton_clicked (self, button):
        pass

    def on_applyButton_clicked (self, button): # pylint: disable-msg=W0613
        self.save()

    def on_helpButton_clicked(self, button): # pylint: disable-msg=W0613
        #import gnome
        #gnome.url_show("file:" + NETCONFDIR + \
        #               "/help/index.html")
        # Fixes Bug 190242 – Firefox instance running as root when
        # used to read docs for system-config-*
        if not self.help_displayed:
            self.help_displayed = True
            
            pw_name = os.getenv("USER")
            uid = None 

            for env in ("SUDO_UID", "USERHELPER_UID"):
                try:
                    uid = os.environ.get(env)
                    uid = int(uid)
                    if uid == 0:
                        continue
                    break
                except:
                    continue
            else:
                uid = os.getuid()
            
            if uid != None:
                import pwd
                # pylint: disable-msg=W0612
                (pw_name, pw_passwd, pw_uid,
                 pw_gid, pw_gecos, pw_dir,
                 pw_shell) = pwd.getpwuid(uid)

            gui_run("/bin/su", [ "su", "-c", 
                    "/usr/bin/htmlview file://" + NETCONFDIR + 
                    "/help/index.html", "-", pw_name])

            self.help_displayed = False

    def on_deviceAddButton_clicked (self, clicked): # pylint: disable-msg=W0613
        interface = NewInterfaceDialog(self.dialog)
        gtk.main()

        if not interface.canceled:
            self.hydrateDevices()
            self.hydrateHardware()

        return (not interface.canceled)

    def on_deviceCopyButton_clicked (self, button): # pylint: disable-msg=W0613
        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return

        srcdev = clist.get_row_data(clist.selection[0])
        df = NCDeviceFactory.getDeviceFactory()
        device = df.getDeviceClass(srcdev.Type, srcdev.SubType)()
        device.apply(srcdev)

        duplicate = True
        num = 0
        devicelist = getDeviceList()
        while duplicate:
            devname = device.DeviceId + 'Copy' + str(num)
            duplicate = False
            for dev in devicelist:
                if dev.DeviceId == devname:
                    duplicate = True
                    break
            num = num + 1
        device.DeviceId = devname
                
        devicelist.append(device)
        device.commit()
        devicelist.commit()
        self.hydrateDevices()

    def on_deviceEditButton_clicked (self, *args): # pylint: disable-msg=W0613
        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return

        device = clist.get_row_data(clist.selection[0])

        if device.Type == LO:
            generic_error_dialog (_('The Loopback device can not be edited!'),
                                  self.dialog)
            return

        self.appBar.push(_("Edit device..."))
        devId = device.DeviceId
        button = self.editDevice(device)

        if button != gtk.RESPONSE_OK and button != 0:
            device.rollback()
            self.appBar.pop()
            return

        device.commit()
        devicelist = getDeviceList()
        devicelist.commit()

        # Fixed change device names in active list of all profiles
        if devId != device.DeviceId:
            profilelist = getProfileList()
            for prof in profilelist:
                if devId in prof.ActiveDevices:
                    pos = prof.ActiveDevices.index(devId)
                    prof.ActiveDevices[pos] = device.DeviceId
            profilelist.commit()

        self.hydrateDevices()
        self.appBar.pop()
        self.checkApply()
        self.on_generic_clist_select_row(\
            clist, clist.selection[0], 0, 0)

    def editDevice(self, device):
        button = 0
        dialog = device.getDialog()
        if dialog:
            dialog.set_transient_for(self.dialog)
            dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            button = dialog.run()
            dialog.destroy()
        else:
            generic_error_dialog (_('The device type %s cannot be edited!') \
                                  % device.Type,
                                  self.dialog)


        return button

    def on_deviceDeleteButton_clicked (self, 
                                       button): # pylint: disable-msg=W0613
        devicelist = getDeviceList()
        profilelist = getProfileList()

        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return

        device = clist.get_row_data(clist.selection[0])

        if device.Type == 'Loopback':
            generic_error_dialog (_('The Loopback device can not be removed!'),
                                  self.dialog)
            return

        buttons = generic_yesno_dialog((_('Do you really want to '
                                          'delete device "%s"?')) % \
                                       str(device.DeviceId),
                                       self.dialog, widget = clist,
                                       page = clist.selection[0])

        if buttons != RESPONSE_YES:
            return

        for prof in profilelist:
            if device.DeviceId in prof.ActiveDevices:
                pos = prof.ActiveDevices.index(device.DeviceId)
                del prof.ActiveDevices[pos]
        profilelist.commit()

       
        del devicelist[devicelist.index(device)]
        devicelist.commit()
        self.hydrateDevices()

    def on_deviceActivateButton_clicked(self, button):
        clist = self.xml.get_widget("deviceList")

        if len(clist.selection) == 0:
            return

        dev = clist.get_row_data(clist.selection[0])
        device = dev.getDeviceAlias()

        gobject.source_remove(self.tag)

        if self.ischanged():
            button = generic_yesno_dialog(
                _("You have made some changes in your configuration.") + "\n"
                  + _("To activate the network device %s, "
                      "the changes have to be saved.") % (device) + "\n"
                  + _("Do you want to continue?"),
                self.dialog)

            if button == RESPONSE_YES:
                if self.save() != 0:
                    return

            if button == RESPONSE_NO:
                return

        dev.activate(dialog = self.dialog)

        if NetworkDevice().find(device):
            self.updateDevicelist()

        self.tag = gobject.timeout_add(4000, self.updateDevicelist)

    def on_deviceDeactivateButton_clicked(self, button):
        clist = self.xml.get_widget("deviceList")
        if len(clist.selection) == 0:
            return

        dev = clist.get_row_data(clist.selection[0])
        device = dev.getDeviceAlias()

        if not device:
            return

        gobject.source_remove(self.tag)

        if self.ischanged():
            button = generic_yesno_dialog(
                _("You have made some changes in your configuration.") + "\n"
                 + _("To deactivate the network device %s, "
                     "the changes have to be saved.") % (device) + "\n\n" 
                 + _("Do you want to continue?"),
                self.dialog)

            if button == RESPONSE_YES:
                if self.save() != 0:
                    return

            if button == RESPONSE_NO:
                return

        #(status, txt) = 
        dev.deactivate(dialog = self.dialog)

        self.updateDevicelist()

        self.tag = gobject.timeout_add(4000, self.updateDevicelist)

    def on_profileMenuItem_activated(self, menu_item, profile):
        if not menu_item or not menu_item.active:
            return

        profilelist = getProfileList()

        if profile == 'default':
            self.xml.get_widget ('profileRenameMenu').set_sensitive (False)
            self.xml.get_widget ('profileDeleteMenu').set_sensitive (False)
        else:
            self.xml.get_widget ('profileRenameMenu').set_sensitive (True)
            self.xml.get_widget ('profileDeleteMenu').set_sensitive (True)

        if not self.no_profileentry_update:
            profilelist.switchToProfile(profile, dochange = True)
            self.initialized = True
            self.hydrate()

        self.checkApply()

    def on_generic_clist_select_row(self, clist, row, 
                                    column, event): # pylint: disable-msg=W0613
        self.edit_button.set_sensitive(True)
        self.delete_button.set_sensitive(True)

        if self.active_page == self.page_num[PAGE_DEVICES]:
            self.copy_button.set_sensitive(True)

        if clist.get_name() == 'hardwareList':
            if len(clist.selection) == 0:
                return
            self.hwsel = clist.get_row_data(clist.selection[0])
            if not self.hwsel:
                return

        if clist.get_name() == 'ipsecList' and \
               self.lastbuttonevent and \
               self.lastbuttonevent.type == gtk.gdk.BUTTON_PRESS:
            info = clist.get_selection_info(int(self.lastbuttonevent.x),
                                            int(self.lastbuttonevent.y))
            if info != None and info[1] == 0:
                profilelist = getProfileList()
                row = info[0]

                ipsec = clist.get_row_data(row)
                name = ipsec.IPsecId

                curr_prof = self.getActiveProfile()

                if ipsec.IPsecId not in curr_prof.ActiveIPsecs:
                    xpm, mask = self.act_xpm, self.act_mask
                    curr_prof = self.getActiveProfile()
                    if curr_prof.ProfileName == 'default':
                        for prof in profilelist:
                            profilelist.activateIpsec(name,
                                                       prof.ProfileName, True)
                    else:
                        profilelist.activateIpsec(name,
                                                   curr_prof.ProfileName,
                                                   True)
                        for prof in profilelist:
                            if prof.ProfileName == "default":
                                continue
                            if name not in prof.ActiveIPsecs:
                                break
                        else:
                            profilelist.activateIpsec(name, 'default', True)

                else:
                    xpm, mask = self.inact_xpm, self.inact_mask
                    if curr_prof.ProfileName == 'default':
                        for prof in profilelist:
                            profilelist.activateIpsec(name, prof.ProfileName,
                                                       False)
                    else:
                        profilelist.activateIpsec(name,
                                                   curr_prof.ProfileName,
                                                   False)
                        profilelist.activateIpsec(name, 'default', False)

                for prof in profilelist:
                    prof.commit()

                clist.set_pixmap(row, PROFILE_COLUMN, xpm, mask)
                self.checkApply()

        if clist.get_name() == 'ipsecList':
            if len(clist.selection) == 0:
                return
            self.ipsel = clist.get_row_data(clist.selection[0])
            if not self.ipsel:
                return

            self.activate_button.set_sensitive(True)
            self.deactivate_button.set_sensitive(True)
            self.delete_button.set_sensitive(True)

        if clist.get_name() == 'deviceList' and \
               self.lastbuttonevent and \
               self.lastbuttonevent.type == gtk.gdk.BUTTON_PRESS:

            info = clist.get_selection_info(int(self.lastbuttonevent.x),
                                            int(self.lastbuttonevent.y))

            if info != None and info[1] == 0:
                row = info[0]
                profilelist = getProfileList()

                device = clist.get_row_data(row)
                name = device.DeviceId
                mtype = device.Type
                if mtype == LO:
                    generic_error_dialog (_('The Loopback device '
                                            'can not be disabled!'),
                                          self.dialog)
                    return

                curr_prof = self.getActiveProfile()

                if device.DeviceId not in curr_prof.ActiveDevices:
                    xpm, mask = self.act_xpm, self.act_mask
                    curr_prof = self.getActiveProfile()
                    if curr_prof.ProfileName == 'default':
                        for prof in profilelist:
                            profilelist.activateDevice(name,
                                                       prof.ProfileName, True)
                    else:
                        profilelist.activateDevice(name,
                                                   curr_prof.ProfileName,
                                                   True)
                        for prof in profilelist:
                            if prof.ProfileName == "default":
                                continue
                            if name not in prof.ActiveDevices:
                                break
                        else:
                            profilelist.activateDevice(name, 'default', True)

                else:
                    xpm, mask = self.inact_xpm, self.inact_mask
                    if curr_prof.ProfileName == 'default':
                        for prof in profilelist:
                            profilelist.activateDevice(name, prof.ProfileName,
                                                       False)
                    else:
                        profilelist.activateDevice(name,
                                                   curr_prof.ProfileName,
                                                   False)
                        profilelist.activateDevice(name, 'default', False)

                for prof in profilelist:
                    prof.commit()

                clist.set_pixmap(row, PROFILE_COLUMN, xpm, mask)
                self.checkApply()

        if clist.get_name() == 'deviceList':
            self.activate_button.set_sensitive(True)
            self.deactivate_button.set_sensitive(True)
            self.delete_button.set_sensitive(True)

            if len(clist.selection) == 0:
                return

            self.devsel = clist.get_row_data(clist.selection[0])
            if not self.devsel:
                return

            curr_prof = self.getActiveProfile()

            try:
                status = clist.get_pixtext(clist.selection[0], STATUS_COLUMN)[0]
            except:
                status = INACTIVE

            if NetworkDevice().find(self.devsel.getDeviceAlias()):
                status = ACTIVE

            if (status == ACTIVE and 
                   (self.devsel.DeviceId in curr_prof.ActiveDevices)):
                #self.activate_button.set_sensitive(False)
                self.activate_button.set_sensitive(True)
                self.deactivate_button.set_sensitive(True)
                self.delete_button.set_sensitive(False)
            else:
                self.activate_button.set_sensitive(True)
                #self.deactivate_button.set_sensitive(False)
                self.deactivate_button.set_sensitive(True)
                self.delete_button.set_sensitive(True)

            if self.devsel.Slave or self.devsel.NMControlled in [None, True]:
                self.activate_button.set_sensitive(False)
                self.deactivate_button.set_sensitive(False)
                self.delete_button.set_sensitive(False)

    def on_generic_clist_unselect_row(self, clist, 
                                      row, column, 
                                      event): # pylint: disable-msg=W0613
        if self.edit_button: 
            self.edit_button.set_sensitive(False)
        #if self.rename_button: self.rename_button.set_sensitive(False)
        if self.delete_button: 
            self.delete_button.set_sensitive(False)
        if self.copy_button: 
            self.copy_button.set_sensitive(False)
        if self.up_button: 
            self.delete_button.set_sensitive(False)
        if self.down_button: 
            self.copy_button.set_sensitive(False)

    def on_generic_clist_button_press_event(self, clist, event, 
                                            *args): # pylint: disable-msg=W0613
        self.lastbuttonevent = event
        #profilelist = getProfileList()

        if event.type == gtk.gdk._2BUTTON_PRESS:  # pylint: disable-msg=W0212
            info = clist.get_selection_info(int(event.x), int(event.y))
            if info != None and not (clist.get_name() in \
                                     [ "deviceList", "ipsecList" ] \
                                     and len(info) >= 2 and info[1] == 0):
                func = self.nop
                if self.editMap.has_key(clist.get_name()):
                    func = self.editButtonFunc[self.editMap[clist.get_name()]]
                mid = clist.connect("button_release_event",
                                   on_generic_clist_button_release_event,
                                   func)
                clist.set_data("signal_id", mid)

    def on_hostnameEntry_changed(self, entry):
        if (self.ignore_widget_changes):
            return
        self.active_profile.DNS.Hostname = entry.get_text()
        self.active_profile.DNS.commit()
        self.checkApply()        
        
    def on_domainEntry_changed(self, entry):
        if (self.ignore_widget_changes):
            return
        self.active_profile.DNS.Domainname = entry.get_text()
        self.active_profile.DNS.commit()
        self.checkApply()

    def on_primaryDnsEntry_changed(self, entry):
        if (self.ignore_widget_changes):
            return
        self.active_profile.DNS.PrimaryDNS = entry.get_text()
        self.active_profile.DNS.commit()
        self.checkApply()

    def on_secondaryDnsEntry_changed(self, entry):
        if (self.ignore_widget_changes):
            return
        self.active_profile.DNS.SecondaryDNS = entry.get_text()
        self.active_profile.DNS.commit()
        self.checkApply()

    def on_tertiaryDnsEntry_changed(self, entry):
        if (self.ignore_widget_changes):
            return
        self.active_profile.DNS.TertiaryDNS = entry.get_text()
        self.active_profile.DNS.commit()
        self.checkApply()

    def on_searchDnsEntry_changed(self, entry):
        if (self.ignore_widget_changes):
            return
        s = entry.get_text()
        newentries = s.split()
        self.active_profile.DNS.SearchList = self.active_profile.\
                                             DNS.SearchList[:0]
        for sp in newentries:
            self.active_profile.DNS.SearchList.append(sp)
            
        self.active_profile.DNS.SearchList.commit()
        self.checkApply()

    def on_hostsAddButton_clicked(self, *args): # pylint: disable-msg=W0613
        # FIXME: Provide possibility to define order from /etc/hosts.conf
        if (self.ignore_widget_changes):
            return
        profilelist = getProfileList()

        curr_prof = self.getActiveProfile()
        if not curr_prof.HostsList:
            curr_prof.createHostsList()
        hostslist = curr_prof.HostsList
        host = Host()
        #clist  = self.xml.get_widget("hostsList")
        dialog = editHostsDialog(host)
        dl = dialog.xml.get_widget ("Dialog")
        dl.set_transient_for(self.dialog)
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        
        button = dialog.run ()
        if button != gtk.RESPONSE_OK and button != 0:
            return

        hostslist.append(host)
        host.commit()
        profilelist.commit()
        self.hydrateProfiles()

    def on_hostsEditButton_clicked (self, *args): # pylint: disable-msg=W0613
        profilelist = getProfileList()

        curr_prof = self.getActiveProfile()
        hostslist = curr_prof.HostsList
        clist  = self.xml.get_widget("hostsList")

        hostsListStore, path = clist.get_selection().get_selected_rows()
        if not path:
            return

        host = hostsListStore.get_value(hostsListStore.get_iter(path[0]), 3)
        
        dialog = editHostsDialog(host)
        dl = dialog.xml.get_widget ("Dialog")
        dl.set_transient_for(self.dialog)
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        
        button = dialog.run ()
        if button != gtk.RESPONSE_OK and button != 0:
            #host.rollback()
            return
            
        try:
            host.commit()
            hostslist.commit()
            profilelist.commit()
        except:
            # we don't want to bother the user every time
            pass
        self.hydrateProfiles()

    def on_hostsDeleteButton_clicked (self, *args): # pylint: disable-msg=W0613
        profilelist = getProfileList()

        clist = self.xml.get_widget('profileList')

        prof = self.getActiveProfile()

        clist = self.xml.get_widget('hostsList')
        hostsListStore, path = clist.get_selection().get_selected_rows()
        if not path:
            return
        
        todel = []
        for p in path:
            todel.append(hostsListStore.get_value(
                            hostsListStore.get_iter(p), 3))
        todel.sort()
        todel.reverse()

        for i in todel:
            prof.HostsList.remove(i)

        profilelist.commit()
        self.hydrateProfiles()

    def on_profileAddMenu_activate (self, *args): # pylint: disable-msg=W0613
        # FIXME: do not reset button state
        dialog = self.xml.get_widget("ProfileNameDialog")
        dialog.set_transient_for(self.dialog)
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        self.xml.get_widget("ProfileName").set_text('')
        dialog.show()
        button = dialog.run()
        dialog.hide()

        if button != gtk.RESPONSE_OK and button != 0:
            return

        profilelist = getProfileList()

        text = self.xml.get_widget("ProfileName").get_text()

        if not text:
            return

        if not re.match("^[a-z|A-Z|0-9]+$", text):
            generic_error_dialog (_('The name may only contain '
                                    'letters and digits!'), self.dialog)
            return 1

        if text == 'default' or text == DEFAULT_PROFILE_NAME:
            generic_error_dialog (_('The profile can\'t be named "%s"!') \
                                  % text, self.dialog)
            return 1

        for prof in profilelist:
            if prof.ProfileName == text:
                generic_error_dialog (_('The profile name already exists!'),
                                      self.dialog)
                return 1

        prof = Profile()
        profilelist.append(prof)
        prof.ProfileName = text
        profilelist.commit()

        profilelist.switchToProfile(prof, dochange = False)

        #self.xml.get_widget("profileList").clear()
        self.initialized = False
        self.hydrateProfiles()
        return 0

    def on_profileCopyMenu_activate (self, *args): # pylint: disable-msg=W0613
        profilelist = getProfileList()

        profile = Profile()
        profile.apply(self.getActiveProfile())
        profile.Active = False
        duplicate = True
        num = 0
        while duplicate:
            profnam = profile.ProfileName + 'Copy' + str(num)
            duplicate = False
            for prof in profilelist:
                if prof.ProfileName == profnam:
                    duplicate = True
                    break
            num = num + 1
        profile.ProfileName = profnam

        profilelist.append(profile)
        profilelist.commit()
        self.initialized = None
        self.hydrateProfiles()

    def on_profileRenameMenu_activate (self, *args): # pylint: disable-msg=W0613
        profilelist = getProfileList()

        profile = self.getActiveProfile()
        if profile.ProfileName == 'default' or \
               profile.ProfileName == DEFAULT_PROFILE_NAME:
            generic_error_dialog (_('The "%s" profile can\'t be renamed!') 
                                  % DEFAULT_PROFILE_NAME,
                                  self.dialog)
            return

        dialog = self.xml.get_widget("ProfileNameDialog")
        dialog.set_transient_for(self.dialog)
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        self.xml.get_widget("ProfileName").set_text(profile.ProfileName)
        dialog.show()
        button = dialog.run()
        dialog.hide()

        if button != gtk.RESPONSE_OK and button != 0:
            return

        text = self.xml.get_widget("ProfileName").get_text()

        if not text:
            return

        if not re.match("^[a-z|A-Z|0-9]+$", text):
            generic_error_dialog (_('The name may only contain '
                                    'letters and digits!'), self.dialog)
            return

        if text == 'default' or text == DEFAULT_PROFILE_NAME:
            generic_error_dialog (_('The profile can\'t be named "%s"!') % 
                                  text, self.dialog)
            return

        for prof in profilelist:
            if prof.ProfileName == text and prof != profile:
                generic_error_dialog (_('The profile name already exists!'),
                                      self.dialog)
                return

        profile.ProfileName = text
        self.initialized = None
        profilelist.commit()
        self.hydrateProfiles()

    def on_profileDeleteMenu_activate (self, *args): # pylint: disable-msg=W0613
        profilelist = getProfileList()

        name = self.getActiveProfile().ProfileName

        if name == 'default' or name == DEFAULT_PROFILE_NAME:
            generic_error_dialog(_('The "%s" Profile '
                                   'can not be deleted!') \
                                 % DEFAULT_PROFILE_NAME,
                                 self.dialog)
            return

        buttons = generic_yesno_dialog((_('Do you really want to '
                                          'delete profile "%s"?')) % str(name),
                                       self.dialog)

        if buttons != RESPONSE_YES:
            return
        
        i = profilelist.index(self.getActiveProfile()) 
        del profilelist[i]
        profilelist.commit()
        profilelist.switchToProfile('default')
        self.initialized = None
        #clist.clear()
        self.hydrate()

    def on_hardwareAddButton_clicked (self, *args): # pylint: disable-msg=W0613
        from netconfpkg.gui.hardwaretype import hardwareTypeDialog
        mtype = hardwareTypeDialog()
        dialog = mtype.xml.get_widget ("Dialog")
        dialog.set_transient_for(self.dialog)
        dialog.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
        button = dialog.run ()
        dialog.destroy()

        if button != gtk.RESPONSE_OK and button != 0:
            return

        hardwarelist = getHardwareList()

        mtype = mtype.Type
        i = hardwarelist.addHardware(mtype)
        hw = hardwarelist[i]        
       
        if self.showHardwareDialog(hw) == gtk.RESPONSE_OK:
            hw.commit()
            hardwarelist.commit()
            self.hydrateHardware()
        else:
            hardwarelist.remove(hw)
        self.hydrateHardware()


    def on_hardwareEditButton_clicked (self, *args): # pylint: disable-msg=W0613
        clist = self.xml.get_widget('hardwareList')

        if len(clist.selection) == 0:
            return

        #type  = clist.get_text(clist.selection[0], 1)
        hardwarelist = getHardwareList()
        #hw = hardwarelist[clist.selection[0]]
        hw = clist.get_row_data(clist.selection[0])
        #type = hw.Type

        if self.showHardwareDialog(hw) == gtk.RESPONSE_OK:
            hw.commit()
            hardwarelist.commit()
        else:
            hw.rollback()
        self.hydrateHardware()

    def showHardwareDialog(self, hw = None):
        dl = None
        if hw:
            dl = hw.getDialog()

        if dl:
            dl.set_transient_for(self.dialog)
            dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            button = dl.run()
            dl.destroy()

            return button

        else:
            generic_error_dialog (_("Sorry, there is nothing to be edited, "
                                    "or this type cannot be edited yet."),
                                  self.dialog)
            return RESPONSE_CANCEL

    def on_hardwareDeleteButton_clicked (self, 
                                         *args): # pylint: disable-msg=W0613
        hardwarelist = getHardwareList()

        clist = self.xml.get_widget("hardwareList")

        if len(clist.selection) == 0:
            return

        hw = clist.get_row_data(clist.selection[0])
        description = hw.Description
        dev = hw.Name

        buttons = generic_yesno_dialog((_('Do you really '
                                          'want to delete "%s"?')) % \
                                       str(description),
                                       self.dialog, widget = clist,
                                       page = clist.selection[0])

        if buttons != RESPONSE_YES:
            return

        # remove hardware
        hardwarelist.remove(hw)
        hardwarelist.commit()  

        buttons = generic_yesno_dialog((_('Do you want to delete '
                                          'all devices that used "%s"?')) % 
                                       str(description),
                                       self.dialog, widget = clist)

        if buttons == RESPONSE_YES:
            # remove all devices that use this hardware
            devicelist = getDeviceList()
            profilelist = getProfileList()
            dlist = []
            for d in devicelist:
                if dev == d.getHWDevice():
                    dlist.append(d)

            for i in dlist:
                for prof in profilelist:
                    if i.DeviceId in prof.ActiveDevices:
                        prof.ActiveDevices.remove(i.DeviceId)
                devicelist.remove(i)

            devicelist.commit()
            self.hydrateDevices()

        self.hydrateHardware()

    def on_about_activate(self, *args): # pylint: disable-msg=W0613
        from version import PRG_VERSION, PRG_NAME, \
                PRG_AUTHORS, PRG_DOCUMENTERS
        if not hasattr(gtk, "AboutDialog"):
            #import gnome.ui
            dlg = gnome.ui.About(PRG_NAME,
                            PRG_VERSION,
                            _("Copyright (c) 2001-2005 Red Hat, Inc."),
                            _("This software is distributed under the GPL. "
                              "Please Report bugs to Red Hat's Bug Tracking "
                              "System: http://bugzilla.redhat.com/"),
                                 ["Harald Hoyer <harald@redhat.com>",
                                  "Than Ngo <than@redhat.com>",
                                  "Philipp Knirsch <pknirsch@redhat.com>",
                                  "Trond Eivind Glomsrød <teg@redhat.com>",
                                  ])
            dlg.set_transient_for(self.dialog)
            dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            dlg.show()
        else:
            dlg = gtk.AboutDialog()
            dlg.set_name(PRG_NAME)
            dlg.set_version(PRG_VERSION)
            dlg.set_copyright(_("Copyright (c) 2001-2005 Red Hat, Inc."))
            dlg.set_authors(PRG_AUTHORS)
            dlg.set_documenters(PRG_DOCUMENTERS)
            dlg.set_translator_credits(_("translator_credits"))
            dlg.set_license(_("This software is distributed under the GPL. \n"
                              "Please Report bugs to Red Hat's Bug Tracking \n"
                              "System: http://bugzilla.redhat.com/"))
            dlg.set_transient_for(self.dialog)
            dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            dlg.run()
            dlg.destroy()

    def on_ipsecAddButton_clicked(self, *args): # pylint: disable-msg=W0613
        ipsecs = getIPsecList()
        ipsec = IPsec()

        canceled = self.ipsecDruid(ipsec)

        if canceled:
            return
        
        ipsecs.append(ipsec)
        ipsec.commit()
        ipsecs.commit()
        self.hydrateIPsec()

    def on_ipsecEditButton_clicked(self, *args): # pylint: disable-msg=W0613
        ipsecs = getIPsecList()
        clist  = self.xml.get_widget("ipsecList")

        if len(clist.selection) == 0:
            return

        ipsec = ipsecs[clist.selection[0]]

        canceled = self.ipsecDruid(ipsec)
        if canceled:
            return
        ipsecs.commit()

        self.hydrateIPsec()

    def ipsecDruid(self, ipsec):
        from netconfpkg.gui.editipsec import editIPsecDruid
        dialog = editIPsecDruid(ipsec)

        dl = dialog.druid

        dl.set_transient_for(self.dialog)
        dl.set_position (gtk.WIN_POS_CENTER_ON_PARENT)

        gtk.main()
        dl.destroy()

        return dialog.canceled

    def on_ipsecDeleteButton_clicked(self, *args): # pylint: disable-msg=W0613
        ipsecs = getIPsecList()

        clist  = self.xml.get_widget("ipsecList")

        if len(clist.selection) == 0:
            return

        del ipsecs[clist.selection[0]]
        ipsecs.commit()
        self.hydrateIPsec()

    def on_ipsecActivateButton_clicked(self, button):
        clist = self.xml.get_widget("ipsecList")

        if len(clist.selection) == 0:
            return

        ipsec = clist.get_row_data(clist.selection[0])

        if self.ischanged():
            button = generic_yesno_dialog(
                _("You have made some changes in your configuration.") + "\n"
                + _("To activate the IPsec connection %s, "
                    "the changes have to be saved.") % (ipsec.IPsecId) 
                + "\n" + _("Do you want to continue?"),
                self.dialog)

            if button == RESPONSE_YES:
                if self.save() != 0:
                    return

            if button == RESPONSE_NO:
                return

        #(status, txt) = 
        ipsec.activate(dialog = self.dialog)

    def on_ipsecDeactivateButton_clicked(self, button):
        clist = self.xml.get_widget("ipsecList")
        if len(clist.selection) == 0:
            return

        ipsec = clist.get_row_data(clist.selection[0])

        if not ipsec:
            return

        if self.ischanged():
            button = generic_yesno_dialog(
                _("You have made some changes in your configuration.") + "\n"
                + _("To deactivate the IPsec connection %s, "
                    "the changes have to be saved.") % (ipsec.IPsecId)
                + "\n" + _("Do you want to continue?"),
                self.dialog)

            if button == RESPONSE_YES:
                if self.save() != 0:
                    return

            if button == RESPONSE_NO:
                return

        ipsec.deactivate(dialog = self.dialog)

__author__ = "Harald Hoyer <harald@redhat.com>"
