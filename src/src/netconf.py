#!/usr/bin/python
# -*- coding: utf-8 -*-

## netconf - A network configuration tool
## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
## Copyright (C) 2001, 2002 Philipp Knirsch <pknirsch@redhat.com>
## Copyright (C) 2001, 2002 Trond Eivind Glomsrød <teg@redhat.com>

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
PROGNAME = 'system-config-network'

import sys
import os
# Just to be safe...
os.umask(0022)

NETCONFDIR = "/usr/share/" + PROGNAME + '/'

if not NETCONFDIR in sys.path:
    sys.path.append(NETCONFDIR)

# Workaround for buggy gtk/gnome commandline parsing python bindings.
__cmdline = sys.argv[1:]
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

os.environ["PYgtk_FATAL_EXCEPTIONS"] = '1'

import os.path
import signal

try:
    from netconfpkg.exception import handleMyException
except RuntimeError, msg:
    print _("Error: %s, %s!") % (PROGNAME, msg)
    if os.path.isfile("/usr/sbin/system-config-network-tui"):
        print _("Starting text version")
        os.execv("/usr/sbin/system-config-network-tui", sys.argv)
    sys.exit(10)


from version import PRG_VERSION
from version import PRG_NAME
from netconfpkg.NC_functions import log
            
from netconfpkg.exception import installExceptionHandler
# FIXME: use action, error, exitcode
#from netconfpkg.exception import action, error, 
# exitcode, installExceptionHandler
    
installExceptionHandler(PROGNAME, PRG_VERSION)

try:
    import gtk
except RuntimeError:
    sys.stderr.write(_("ERROR: Unable to initialize graphical environment."
                       "Most likely cause of failure is that the tool was "
                       "not run using a graphical environment. Please either "
                       "start your graphical user interface or set your "
                       "DISPLAY variable."))
    sys.exit(0)

def get_pixpath(pixmap_file):
    fn = pixmap_file
    search_path = [ "",
                    "pixmaps/",
                    "../pixmaps/",
                    NETCONFDIR,
                    NETCONFDIR + "pixmaps/",
                    "/usr/share/pixmaps/" ]
    for sp in search_path:
        pixmap_file = sp + fn
        if os.path.exists(pixmap_file):
            break
    else:
        return None

    return pixmap_file

def splash_screen(gfx = None):
    if gfx:
        window = gtk.Window(gtk.WINDOW_POPUP)
        window.set_title(PRG_NAME)
        window.set_position (gtk.WIN_POS_CENTER)
        window.show_all()
        window.show_now()
        while gtk.events_pending():
            gtk.main_iteration()
        pixmap_wid = gtk.Image()
        pixfile = get_pixpath("system-config-network-splash.png")
        if not pixfile:
            return None
        pixmap_wid.set_from_file(pixfile)
        window.add(pixmap_wid)
        pixmap_wid.show_all()
        pixmap_wid.show_now()
    else:
        window = gtk.Window(gtk.WINDOW_POPUP)
        window.set_title(PRG_NAME)
        window.set_position (gtk.WIN_POS_CENTER)
        window.set_border_width(5)
        lbl = gtk.Label(_('Loading Network Configuration...'))
        window.add(lbl)
        lbl.show_now()

    window.show_all()
    window.show_now()

    while gtk.events_pending():
        gtk.main_iteration()

    return window

def Usage():
    print _("system-config-network - network configuration tool\n\n"
            "Usage: system-config-network -v --verbose")

def runit(splash = None):
    from netconfpkg import NC_functions
    from netconfpkg.NCException import NCException
    splash_window = None

    try:
        if splash:
            splash_window = splash_screen(True)
        import gnome        
        import netconfpkg.gui.GUI_functions
        import netconfpkg
        netconfpkg.PRG_NAME = PRG_NAME
        from netconfpkg.gui.NewInterfaceDialog import NewInterfaceDialog
        from netconfpkg.gui.maindialog import mainDialog

        netconfpkg.gui.GUI_functions.PROGNAME = PROGNAME

        # make ctrl-C work
        signal.signal (signal.SIGINT, signal.SIG_DFL)

        progname = os.path.basename(sys.argv[0])

        gnome.program_init(PROGNAME, "scn")
        gtk.glade.bindtextdomain(PROGNAME, "/usr/share/locale")

        if progname == 'system-config-network-druid' or \
               progname == 'internet-druid':
            interface = NewInterfaceDialog()
            gtk.main()
            if interface.canceled:
                sys.exit(1)

        window = mainDialog() # pylint: disable-msg=W0612

        if splash_window:
            splash_window.destroy()
            del splash_window

        gtk.main()

    except NCException, e:
        NC_functions.generic_error_dialog(str(e))
        return
    except:
        handleMyException(sys.exc_info(), PROGNAME, PRG_VERSION)

class BadUsage(Exception): 
    pass

def main(cmdline):
    import getopt
    from netconfpkg import NC_functions
    NC_functions.setVerboseLevel(2)
    NC_functions.setDebugLevel(0)
    hotshot = 0
    splash = 0
    chroot = None

    try:
        opts = getopt.getopt(cmdline, "vh?r:d",
                                   [
                                    "verbose",
                                    "debug",
                                    "help",
                                    "hotshot",
                                    "splash",
                                    "root="
                                    ])[0]
        for opt, val in opts:
            if opt == '-v' or opt == '--verbose':
                NC_functions.setVerboseLevel(NC_functions.getVerboseLevel()+1)
                continue

            if opt == '-d' or opt == '--debug':
                NC_functions.setDebugLevel(NC_functions.getDebugLevel()+1)
                continue

            if opt == '--hotshot':
                hotshot += 1
                continue

            if opt == '--splash':
                splash += 1
                continue

            if opt == '-h' or opt == "?" or opt == '--help':
                Usage()
                return 0

            if opt == '-r' or opt == '--root':
                chroot = val
                continue

            raise BadUsage

    except (getopt.error, BadUsage):
        Usage()
        return 1

    if not NC_functions.getDebugLevel():
        log.handler = log.syslog_handler
        log.open()
    else:
        log.handler = log.file_handler
        log.open(sys.stderr)

    if chroot:
        NC_functions.setRoot(chroot)

    if not os.access(NC_functions.getRoot(), os.W_OK):
        if os.getuid() != 0:
            from netconfpkg.gui import GUI_functions
            NC_functions.generic_error_dialog (
                                _("Please start system-config-network "
                                  "with root permissions!\n"))
            return 10

    if chroot:
        NC_functions.prepareRoot(chroot)


    if hotshot:
        import tempfile
        from hotshot import Profile
        import hotshot.stats
        (fd, filename) = tempfile.mkstemp()
        prof = Profile(filename)
        prof = prof.runcall(runit)
        s = hotshot.stats.load(filename)
        s.strip_dirs().sort_stats('time').print_stats(20)
        s.strip_dirs().sort_stats('cumulative').print_stats(20)
        os.close(fd)
        os.unlink(filename)
    else:
        runit(splash)

    return 0

if __name__ == '__main__':
    sys.exit(main(__cmdline))

__author__ = "Harald Hoyer <harald@redhat.com>"
