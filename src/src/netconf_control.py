#! /usr/bin/python
# -*- coding: utf-8 -*-
## redhat-network-control - A easy-to-use interface for configuring/activating
## Copyright (C) 2002 Red Hat, Inc.
## Copyright (C) 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2003-2005 Harald Hoyer <harald@redhat.com>

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

import sys

PROGNAME = 'system-config-network'

NETCONFDIR = "/usr/share/" + PROGNAME + '/'

if not NETCONFDIR in sys.path:
    sys.path.append(NETCONFDIR)

# Workaround for buggy gtk/gnome commandline parsing python bindings.
cmdline = sys.argv[1:]
sys.argv = sys.argv[:1]

import locale
try:
    locale.setlocale (locale.LC_ALL, "")
except locale.Error, e:
    import os
    os.environ['LC_ALL'] = 'C'
    locale.setlocale (locale.LC_ALL, "")
import gettext
gettext.bind_textdomain_codeset(PROGNAME,locale.nl_langinfo(locale.CODESET))
gettext.bindtextdomain(PROGNAME, '/usr/share/locale')
gettext.textdomain(PROGNAME)
_ = lambda x: gettext.lgettext(x)
import __builtin__
__builtin__.__dict__['_'] = _

import signal
import os
import os.path

try:
    import gtk
except RuntimeError:
    sys.stderr.write(_("""\
ERROR: Unable to initialize graphical environment. 
Most likely cause of failure is that the tool was not run using a graphical
environment. Please either start your graphical user interface or set your
DISPLAY variable.
"""))
    sys.exit(0)

from  gtk import glade
import gobject
from netconfpkg import NC_functions
from netconfpkg.gui import GUI_functions
from netconfpkg.NC_functions import (
     DEFAULT_PROFILE_NAME, getRoot,
    _, ACTIVE, INACTIVE,
    generic_longinfo_dialog, generic_error_dialog, generic_run_dialog)
from netconfpkg.Control import NetworkDevice
from netconfpkg.gui.GUI_functions import ( 
    GLADEPATH, 
    xml_signal_autoconnect, 
    get_icon, get_pixbuf, load_icon)
from netconfpkg import NCDeviceList, NCProfileList
from netconfpkg.NCDeviceList import getDeviceList
from netconfpkg.NCProfileList import getProfileList

STATUS_COLUMN = 0
DEVICE_COLUMN = 1
NICKNAME_COLUMN = 2

class mainDialog:
    def __init__(self):
        glade_file = 'neat-control.glade'

        if not os.path.isfile(glade_file):
            glade_file = GLADEPATH + glade_file
        if not os.path.isfile(glade_file):
            glade_file = NETCONFDIR + glade_file

        self.isRoot = False
        self.no_profileentry_update = False
        
        if os.access(getRoot() + "/", os.W_OK):
            self.isRoot = True

        self.xml = glade.XML(glade_file, None, domain=PROGNAME)

        xml_signal_autoconnect(self.xml,
            {
            'on_closeButton_clicked' : self.on_closeButton_clicked,
            'on_infoButton_clicked' : self.on_infoButton_clicked,
            'on_activateButton_clicked' : self.on_activateButton_clicked,
            'on_deactivateButton_clicked' : self.on_deactivateButton_clicked,
            'on_configureButton_clicked' : self.on_configureButton_clicked,
            'on_monitorButton_clicked' : self.on_monitorButton_clicked,
            'on_profileActivateButton_clicked' : \
            self.on_profileActivateButton_clicked,
#            'on_autoSelectProfileButton_clicked' : \
#            self.on_autoSelectProfileButton_clicked,
            'on_interfaceClist_select_row' : (\
            self.on_generic_clist_select_row,
            self.xml.get_widget('activateButton'),
            self.xml.get_widget('deactivateButton'),
            self.xml.get_widget('editButtonbutton'),
            self.xml.get_widget('monitorButton')),
            })

        self.dialog = self.xml.get_widget('mainWindow')
        self.dialog.connect('delete-event', self.on_Dialog_delete_event)
        self.dialog.connect('hide', gtk.main_quit)
        self.on_xpm, self.on_mask = get_icon('on.xpm')
        self.off_xpm, self.off_mask = get_icon('off.xpm')

        if not os.access('/usr/bin/rp3', os.X_OK):
            self.xml.get_widget('monitorButton').hide()

        load_icon('neat-control.xpm', self.dialog)
        pix = self.xml.get_widget('pixmap')
        pix.set_from_pixbuf(get_pixbuf('neat-control-logo.png'))
        clist = self.xml.get_widget('interfaceClist')
        clist.column_titles_passive ()

        self.devicelist = self.getProfDeviceList()
        self.activedevicelist = NetworkDevice().get()
        self.hydrate()
        self.oldprofile = None
        self.xml.get_widget('profileActivateButton').set_sensitive(False)
        self.hydrateProfiles()

        self.xml.get_widget('autoSelectProfileButton').hide()

        self.tag = gobject.timeout_add(4000, self.update_dialog)
        # Let this dialog be in the taskbar like a normal window
        self.dialog.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_NORMAL)
        self.dialog.show()

    def on_Dialog_delete_event(self, *args): # pylint: disable-msg=W0613
        self.dialog = None
        gtk.main_quit()

    def on_closeButton_clicked(self, button): # pylint: disable-msg=W0613
        self.dialog = None
        gtk.main_quit()

    def on_infoButton_clicked(self, button): # pylint: disable-msg=W0613
        from version import PRG_VERSION
        from version import PRG_NAME
        if not hasattr(gtk, "AboutDialog"):
            import gnome.ui
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
            dlg.set_authors(["Harald Hoyer <harald@redhat.com>",
                             "Than Ngo <than@redhat.com>",
                             "Philipp Knirsch <pknirsch@redhat.com>",
                             "Trond Eivind Glomsrød <teg@redhat.com>",
                             ])
            dlg.set_documenters(["Tammy Fox <tfox@redhat.com>"])
            dlg.set_copyright(_(
                "This software is distributed under the GPL. \n"
                "Please Report bugs to Red Hat's Bug Tracking \n"
                "System: http://bugzilla.redhat.com/"))
            dlg.set_transient_for(self.dialog)
            dlg.set_position (gtk.WIN_POS_CENTER_ON_PARENT)
            dlg.run()
            dlg.destroy()

    def on_activateButton_clicked(self, button): # pylint: disable-msg=W0613
        device = self.clist_get_device()
        nickname = self.clist_get_nickname()

        for dev in getDeviceList():
            if dev.DeviceId == nickname:
                break
        else:
            return

        gobject.source_remove(self.tag)

        if device:
            dev.activate()                         # pylint: disable-msg=W0631
            self.update_dialog()

        self.tag = gobject.timeout_add(4000, self.update_dialog)

    def on_deactivateButton_clicked(self, button): # pylint: disable-msg=W0613
        device = self.clist_get_nickname()
        for dev in getDeviceList():
            if dev.DeviceId == device:
                break
        else:
            return

        # pylint: disable-msg=W0631
        if dev and device:
            dev.deactivate()
            self.update_dialog()

    def on_configureButton_clicked(self, button): # pylint: disable-msg=W0613
        device = self.clist_get_nickname()
        if not device:
            return

        for dev in getDeviceList():
            if dev.DeviceId == device:
                break
        else:
            return

        # pylint: disable-msg=W0631

        (ret, msg) = dev.configure()

        if not self.dialog:
            return False

        if ret:
            errorString = _('Cannot configure network device %s')\
                          % (device)
            generic_longinfo_dialog(errorString, msg, self.dialog)

        # update dialog #83640
        # Re-read the device list
        self.devicelist = self.getProfDeviceList(refresh=True)
        self.activedevicelist = NetworkDevice().get()
        # Update the gui
        self.hydrateProfiles(refresh = True)
        self.hydrate()
        self.oldprofile = None # forces a re-read of oldprofile
        self.update_dialog()

    def on_profileActivateButton_clicked(self, 
                                         button): # pylint: disable-msg=W0613
        profile = self.get_active_profile().ProfileName

        generic_run_dialog(
            command = "/usr/bin/system-config-network-cmd",
            argv = [ "system-config-network-cmd", "-a", "-p", profile ],
            title = _("Switching Profiles"),
            label = _("Switching to profile %s") % profile,
            errlabel = _("Failed to switch to profile %s") % profile,
            dialog = self.dialog)


        # Re-read the device list
        self.devicelist = self.getProfDeviceList(refresh=True)
        self.activedevicelist = NetworkDevice().get()
        # Update the gui
        self.hydrate()
        self.oldprofile = None # forces a re-read of oldprofile
        self.hydrateProfiles()
        self.update_dialog()

    def on_monitorButton_clicked(self, button): # pylint: disable-msg=W0613
        # TBD
        generic_error_dialog(_("To be rewritten!"))
        return

    def on_generic_clist_select_row(self, clist, 
                                row, column, event, # pylint: disable-msg=W0613
                                    activate_button = None,
                                    deactivate_button = None,
                                    configure_button = None,
                                    monitor_button = None):
        if len(clist.selection) == 0:
            return

        status = self.clist_get_status()
        devname = self.clist_get_nickname()
        dev = None
        for dev in getDeviceList():
            if dev.DeviceId == devname:
                break
        else:
            dev = None

        # pylint: disable-msg=W0631

        if dev and (dev.AllowUser or self.isRoot):
            self.xml.get_widget('activateButton').set_sensitive(True)
            self.xml.get_widget('deactivateButton').set_sensitive(True)
        else:
            self.xml.get_widget('activateButton').set_sensitive(False)
            self.xml.get_widget('deactivateButton').set_sensitive(False)

        if status == ACTIVE:
            #self.xml.get_widget('activateButton').set_sensitive(False)
            #self.xml.get_widget('deactivateButton').set_sensitive(True)
            #self.xml.get_widget('configureButton').set_sensitive(False)
            self.xml.get_widget('monitorButton').set_sensitive(True)
        else:
            #self.xml.get_widget('activateButton').set_sensitive(True)
            #self.xml.get_widget('deactivateButton').set_sensitive(False)
            #self.xml.get_widget('configureButton').set_sensitive(True)
            self.xml.get_widget('monitorButton').set_sensitive(False)

    def clist_get_status(self):
        status = INACTIVE
        clist = self.xml.get_widget('interfaceClist')
        if len(clist.selection) == 0:
            return
        try:
            status = clist.get_pixtext(clist.selection[0], STATUS_COLUMN)[0]
        except ValueError:
            status = clist.get_text(clist.selection[0], STATUS_COLUMN)
        return status

    def clist_get_device(self):
        dev = None
        clist = self.xml.get_widget('interfaceClist')
        if len(clist.selection) == 0:
            return
        try:
            dev = clist.get_pixtext(clist.selection[0], DEVICE_COLUMN)[0]
        except ValueError:
            dev = clist.get_text(clist.selection[0], DEVICE_COLUMN)
            
        return dev

    def clist_get_nickname(self):
        nick = None
        clist = self.xml.get_widget('interfaceClist')
        if len(clist.selection) == 0:
            return
        nick = clist.get_text(clist.selection[0], NICKNAME_COLUMN)
        return nick

    def hydrate(self):
        clist = self.xml.get_widget('interfaceClist')
        clist.clear()
        clist.set_row_height(20)
        status_pixmap = self.off_xpm
        status_mask = self.off_mask
        status = INACTIVE
        row = 0

        for dev in self.devicelist:
            # skip slave devices and those controlled
            # by NetworkManager
            if dev.Slave or dev.NMControlled:
                continue
                
            devname = dev.Device            
            if dev.Alias and dev.Alias != "":
                devname = devname + ':' + str(dev.Alias)

            if (devname in self.activedevicelist or \
                   dev.DeviceId in self.activedevicelist):
                status = ACTIVE
                status_pixmap = self.on_xpm
                status_mask = self.on_mask
            else:
                status = INACTIVE
                status_pixmap = self.off_xpm
                status_mask = self.off_mask

            device_pixmap, device_mask = GUI_functions.get_device_icon_mask(
                dev.Type, self.dialog)

            clist.append([status, devname, dev.DeviceId])
            clist.set_pixtext(row, STATUS_COLUMN, status, 5, status_pixmap,
                              status_mask)
            clist.set_pixtext(row, DEVICE_COLUMN, devname, 5, device_pixmap,
                              device_mask)
            row = row + 1

        self.on_generic_clist_select_row(clist, 0, 0, 0)

    def hydrateProfiles(self, refresh = None):
        profilelist = getProfileList(refresh)

        self.no_profileentry_update = True
        omenu = self.xml.get_widget('profileOption')

        if len(profilelist) == 1:
            self.xml.get_widget('profileFrame').hide()

        if omenu:
            omenu.remove_menu ()

        menu = gtk.Menu ()
        history = 0
        i = 0
        for prof in profilelist:
            name = prof.ProfileName
            # change the default profile to a more understandable name
            if name == "default":
                name = DEFAULT_PROFILE_NAME
            if prof.Active == True:
                name += _(" (active)")
            menu_item = gtk.MenuItem (name)
            menu_item.show ()
            menu_item.connect ("activate",
                               self.on_profileMenuItem_activated,
                               prof.ProfileName)
            menu.append (menu_item)
            if prof.ProfileName == self.get_active_profile().ProfileName:
                history = i
                if self.oldprofile == None:
                    self.oldprofile = prof.ProfileName
            i = i+1
        if self.get_active_profile().ProfileName != self.oldprofile:
            self.xml.get_widget('interfaceClist').set_sensitive(False)
        else:
            self.xml.get_widget('interfaceClist').set_sensitive(True)
        menu.show ()

        if omenu:
            omenu.set_menu (menu)
            omenu.set_history (history)

        menu.get_children()[history].activate ()
        self.no_profileentry_update = False

    def get_active_profile(self):
        profilelist = getProfileList()
        return profilelist.getActiveProfile()

    def set_profile_active(self, profile):
        profilelist = getProfileList ()
        for prof in profilelist:
            if prof.ProfileName == profile:
                prof.Active = True
                #print "profile " + prof.ProfileName + " activated\n"
            else: prof.Active = False
            prof.commit()

    def getProfDeviceList(self, refresh=None):
        profilelist = getProfileList(refresh)
        prof = profilelist.getActiveProfile()
        devlist = getDeviceList(refresh)
        activedevlist = []
        for devid in prof.ActiveDevices:
            for dev in devlist:
                if dev.DeviceId != devid:
                    continue
                break
            else:
                continue                    
            activedevlist.append(dev) # pylint: disable-msg=W0631
        return activedevlist

    def on_profileMenuItem_activated(self, 
                            menu_item, profile): # pylint: disable-msg=W0613
        if not self.no_profileentry_update:
            self.set_profile_active(profile)
            if self.oldprofile != self.get_active_profile().ProfileName:
                self.xml.get_widget('profileActivateButton' \
                                    ).set_sensitive(True)
                self.xml.get_widget('interfaceClist').set_sensitive(False)
                self.xml.get_widget('activateButton').set_sensitive(False)
                self.xml.get_widget('deactivateButton').set_sensitive(False)
            else:
                self.xml.get_widget('profileActivateButton' \
                                    ).set_sensitive(False)
                self.xml.get_widget('interfaceClist').set_sensitive(True)
                self.xml.get_widget('activateButton').set_sensitive(True)
                self.xml.get_widget('deactivateButton').set_sensitive(True)

    def update_dialog(self):
        if not self.dialog:
            return False
        activedevicelistold = self.activedevicelist
        self.activedevicelist = NetworkDevice().get()

        if activedevicelistold != self.activedevicelist:
            self.hydrate()
            return True

        return True

def Usage():
    # FIXME: change string
    print _("system-config-network - network configuration tool\n\n"
            "Usage: system-config-network -v --verbose -d --debug")

if __name__ == '__main__':
    # make ctrl-C work
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if os.getuid() == 0:
        NCProfileList.updateNetworkScripts()
        NCDeviceList.updateNetworkScripts()
    import getopt
    class BadUsage(Exception):
        pass

    try:
        __opts, __args = getopt.getopt(cmdline, "v?d",
                                   [
                                    "verbose",
                                    "debug",
                                    "help",
                                    "root="
                                    ])
        for __opt, __val in __opts:
            if __opt == '-v' or __opt == '--verbose':
                NC_functions.setVerboseLevel(NC_functions.getVerboseLevel()+1)
                continue

            if __opt == '-d' or __opt == '--debug':
                NC_functions.setDebugLevel(NC_functions.getDebugLevel()+1)
                continue

            if __opt == '-h' or __opt == "?" or __opt == '--help':
                Usage()
                sys.exit(0)

    except (getopt.error, BadUsage):
        Usage()
        sys.exit(1)

    window = mainDialog()
    gtk.main()

    sys.exit(0)
    
__author__ = "Harald Hoyer <harald@redhat.com>, Than Ngo <than@redhat.com>"
