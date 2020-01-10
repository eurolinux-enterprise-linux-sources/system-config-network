#!/usr/bin/python
# -*- coding: utf-8 -*-

## netconf-tui - a tui network configuration tool
## Copyright (C) 2002-2003 Red Hat, Inc.
## Copyright (C) 2002-2003 Trond Eivind Glomsrød <teg@redhat.com>
## Copyright (C) 2002-2005 Harald Hoyer <harald@redhat.com>

#from snack import *

PROGNAME = 'system-config-network'

import os
import sys
import locale
import gettext
import signal

from snack import SnackScreen
import netconfpkg # pylint: disable-msg=W0611
from netconfpkg import NC_functions
from netconfpkg.NC_functions import log, generic_error_dialog
from netconfpkg.NCDeviceList import getDeviceList
from netconfpkg.NCProfileList import getProfileList

try:
    locale.setlocale (locale.LC_ALL, "")
except locale.Error, e:
    import os
    os.environ['LC_ALL'] = 'C'
    locale.setlocale (locale.LC_ALL, "")
gettext.bind_textdomain_codeset(PROGNAME,locale.nl_langinfo(locale.CODESET))
gettext.bindtextdomain(PROGNAME, '/usr/share/locale')
gettext.textdomain(PROGNAME)
_ = lambda x: gettext.lgettext(x)
import __builtin__
__builtin__.__dict__['_'] = _

if not "/usr/share/system-config-network" in sys.path:
    sys.path.append("/usr/share/system-config-network")

if not "/usr/share/system-config-network/netconfpkg/" in sys.path:
    sys.path.append("/usr/share/system-config-network/netconfpkg")

from version import PRG_VERSION
from version import PRG_NAME
import traceback
import types
import getopt
class BadUsage(Exception):
    pass

_dumpHash = {}


def ddump(file_fd, level, value, first):
    for k, v in value.items():
        if not first:
            file_fd.write(", ")
        else:
            first = 0
        if type(k) == types.StringType:
            file_fd.write("'%s': " % (k, ))
        else:
            file_fd.write("%s: " % (k, ))
        if type(v) == types.InstanceType:
            dumpClass(v, file_fd, level + 1)
        else:
            file_fd.write("%s" % (v, ))

def ddump2(file_fd, level, value, first):
    for item in value:
        if not first:
            file_fd.write(", ")
        else:
            first = 0
        if type(item) == types.InstanceType:
            dumpClass(item, file_fd, level + 1)
        else:
            file_fd.write("%s" % (item, ))
    return first

# XXX do length limits on obj dumps.
def dumpClass(instance, file_fd, level=0):
    # protect from loops
    if not _dumpHash.has_key(instance):
        _dumpHash[instance] = None
    else:
        file_fd.write("Already dumped\n")
        return
    if (instance.__class__.__dict__.has_key("__str__") or
        instance.__class__.__dict__.has_key("__repr__")):
        file_fd.write("%s\n" % (instance,))
        return
    file_fd.write("%s instance, containing members:\n" %
             (instance.__class__.__name__))
    pad = ' ' * ((level) * 2)
    for key, value in instance.__dict__.items():
        if type(value) == types.ListType:
            file_fd.write("%s%s: [" % (pad, key))
            first = 1
            first = ddump2(file_fd, level, value, first)
            file_fd.write("]\n")
        elif type(value) == types.DictType:
            file_fd.write("%s%s: {" % (pad, key))
            first = 1
            ddump(file_fd, level, value, first)
            file_fd.write("}\n")
        elif type(value) == types.InstanceType:
            file_fd.write("%s%s: " % (pad, key))
            dumpClass(value, file_fd, level + 1)
        else:
            file_fd.write("%s%s: %s\n" % (pad, key, value))

#
# handleException function
#
def handleException((mtype, value, tb), progname, version):
    mlist = traceback.format_exception (mtype, value, tb)
    tblast = traceback.extract_tb(tb, limit=None)
    if len(tblast):
        tblast = tblast[len(tblast)-1]
    extxt = traceback.format_exception_only(mtype, value)
    text = "Component: %s\n" % progname
    text = text + "Version: %s\n" % version
    text = text + "Summary: TB "
    text = _("An unhandled exception has occured.  This "
             "is most likely a bug.  Please save the crash "
             "dump and file a detailed bug "
             "report against system-config-network at "
             "https://bugzilla.redhat.com/bugzilla") + "\n" + text

    if tblast and len(tblast) > 3:
        tblast = tblast[:3]
    for t in tblast:
        text = text + str(t) + ":"
    text = text + extxt[0]
    text = text + "".join(mlist)

    print text
    import pdb
    pdb.post_mortem (tb)
    os.kill(os.getpid(), signal.SIGKILL)

    sys.exit(10)

sys.excepthook = lambda type, value, tb: handleException((type, value, tb),
                                                         PRG_NAME, PRG_VERSION)



from netconfpkg import exception
from netconfpkg.NCHardwareList import getHardwareList
from snack import GridForm, TextboxReflowed, Listbox, ButtonBar, Entry, Grid, Label
from netconfpkg.NC_functions import ETHERNET, ISDN, MODEM, QETH
from netconfpkg.NCDeviceFactory import getDeviceFactory

# load all plugins by importing the base module directory
import netconfpkg.tui # pylint: disable-msg=W0611

def loadConfig(mscreen):
    exception.action(_("Loading configuration"))
    t = TextboxReflowed(10, _("Loading Device Configuration"))
    g = GridForm(mscreen, _("Network Configuration"), 1, 1)
    g.add(t, 0, 0)
    g.draw()
    mscreen.refresh()
    devicelist = getDeviceList() # pylint: disable-msg=W0612
    t.setText(_("Loading Hardware Configuration"))
    g.draw()
    mscreen.refresh()
    hardwarelist = getHardwareList() # pylint: disable-msg=W0612
    t.setText(_("Loading Profile Configuration"))
    g.draw()
    mscreen.refresh()
    profilelist = getProfileList() # pylint: disable-msg=W0612
    mscreen.popWindow()

#
# main Screen
#
def usage():
    print _("system-config-network - network configuration tool\n\n"
            "Usage: system-config-network -v --verbose -d --debug")


def parse_opts():
    NC_functions.setVerboseLevel(2)
    NC_functions.setDebugLevel(0)
    chroot = None
    
    # FIXME: add --root= option
    
    try:
        opts = getopt.getopt(sys.argv[1:], "vh?r:d",
                                   [
                                    "verbose",
                                    "debug",
                                    "help",
                                    "root="
                                    ])[0]
        for opt, val in opts:
            if opt == '-v' or opt == '--verbose':
                NC_functions.setVerboseLevel(NC_functions.getVerboseLevel()+1)
                continue
    
            if opt == '-d' or opt == '--debug':
                NC_functions.setDebugLevel(NC_functions.getDebugLevel()+1)
                continue
    
            if opt == '-h' or opt == "?" or opt == '--help':
                usage()
                sys.exit(0)
    
            if opt == '-r' or opt == '--root':
                chroot = val
                continue
    
            raise BadUsage
    
    except (getopt.error, BadUsage):
        usage()
        return sys.exit(1)
    
    
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
            generic_error_dialog (_("Please start system-config-network "
                                    "with root permissions!\n"))
            sys.exit(10)
    
    if chroot:
        NC_functions.prepareRoot(chroot)

def selectAction(mscreen, plist):
    from netconfpkg.tui import NCPluginDNS
    from netconfpkg.tui import NCPluginDevices
    li = Listbox(5, returnExit=1)
    l = 0
    le = mscreen.width - 6
    if le <= 0: 
        le = 5
    # do this more inteligent - auto loading of new plugins??
    for act, act_id in { \
        _("Device configuration") : NCPluginDevices.NCPluginDevicesTui(plist),
        _("DNS configuration") : NCPluginDNS.NCPluginDNSTui(plist),
        }.items():
    
       li.append(act, act_id)
       l += 1
    if not l:
        return None

    g = GridForm(mscreen, _("Select Action"), 1, 3)
    bb = ButtonBar(mscreen, ((_("Save&Quit"), "save"), (_("Quit"), "cancel")))
    g.add(li, 0, 1)
    g.add(bb, 0, 2, growx=1)
    res = g.run()
    mscreen.popWindow()
    if bb.buttonPressed(res) == "save":
        ret = -1
    elif bb.buttonPressed(res) == "cancel":
        ret = None
    else:
        ret = li.current()
        if not ret:
            pass
    return ret
    
#
# __main__
#
def main():
    parse_opts()
    screen = SnackScreen()
    plist = getProfileList()
    devlist = getDeviceList()
    try:
        #mainScreen(screen)
        loadConfig(screen)
        while True:
            act = selectAction(screen, plist)
            if act:
                if act == -1:
                    # save and exit
                    if devlist.modified():
                        devlist.save()
                    if plist.modified():
                        plist.save()
                    break
                if hasattr(act, "runIt"):
                    if act.runIt(screen):
                        plist.commit()
                    else:
                        pass
                else:
                    # we shouldn't get here
                    pass
            else:
                break
                

        screen.finish()
        #print dir(screen)
        #print dev
    except SystemExit, code:
        screen.finish()
        return code
    except:
        screen.finish()
        raise

if __name__ == "__main__":
    sys.exit(main())

__author__ = str("Trond Eivind Glomsrød <teg@redhat.com>,"
                 " Harald Hoyer <harald@redhat.com>")

                 
                 
                 
                 
