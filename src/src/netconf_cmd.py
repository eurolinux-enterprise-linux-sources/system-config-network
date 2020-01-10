#! /usr/bin/python
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

import sys

if not "/usr/share/system-config-network" in sys.path:
    sys.path.append("/usr/share/system-config-network")

if not "/usr/share/system-config-network/netconfpkg/" in sys.path:
    sys.path.append("/usr/share/system-config-network/netconfpkg")

# Workaround for buggy gtk/gnome commandline parsing python bindings.
cmdline = sys.argv[1:]

import getopt
import signal
import os
import os.path
from netconfpkg import Control
from netconfpkg import NC_functions
#from netconfpkg.genClass import ParseError
from version import PRG_VERSION

PROGNAME = 'system-config-network'

class ParseError(Exception):
    pass

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

def handleException((mtype, value, tb), progname, version, debug=None):
    import pdb
    import traceback
    mlist = traceback.format_exception (mtype, value, tb)
    tblast = traceback.extract_tb(tb, limit=None)
    if len(tblast):
        tblast = tblast[len(tblast)-1]
    extxt = traceback.format_exception_only(mtype, value)
    text = _("An unhandled exception has occured.  This "
            "is most likely a bug.\nPlease file a detailed bug "
            "report against the component %s at \n"
            "https://bugzilla.redhat.com/bugzilla\n"
             "using the text below.\n") % \
            progname
    text += "Component: %s\n" % progname
    text += "Version: %s\n" % version
    text += "Summary: TB "
    if tblast and len(tblast) > 3:
        tblast = tblast[:3]
    for t in tblast:
        text += str(t) + ":"
    text += extxt[0]
    text += "".join(mlist)

    trace = tb
    while trace.tb_next:
        trace = trace.tb_next
    frame = trace.tb_frame
    text += ("\nLocal variables in innermost frame:\n")
    try:
        for (key, value) in frame.f_locals.items():
            text += "%s: %s\n" % (key, value)
    except:
        pass

    sys.stderr.write(text)
    if debug:
        pdb.post_mortem (tb)
        os.kill(os.getpid(), signal.SIGKILL)
    sys.exit(10)


def Usage():
    sys.stderr.write(_("%s - network configuration commandline tool") 
                     % (sys.argv[0]) + '\n')
    sys.stderr.write(_("Copyright (c) 2001-2005 Red Hat, Inc.") + '\n')
    sys.stderr.write( _("This software is distributed under the GPL. "
            "Please Report bugs to Red Hat's Bug Tracking "
            "System: http://bugzilla.redhat.com/") + "\n\n")
    sys.stderr.write(_("Usage: %s") % (sys.argv[0]) + '\n')
    sys.stderr.write( "\t-p, --profile <profile> [--activate, -a]: %s"
                      % _("switch / activate profile") + '\n')
    sys.stderr.write( "\t-h, --hardwarelist : %s"
                      % _("export / import hardware list") + '\n')
    sys.stderr.write( "\t-s, --ipseclist : %s"
                      % _("export / import IPsec list") + '\n')
    sys.stderr.write( "\t-d, --devicelist   : %s"
                      % _("export / import device list (default)") + '\n')
    sys.stderr.write( "\t-o, --profilelist  : %s"
                      % _("export / import profile list") + '\n')
    sys.stderr.write( "\t-r, --root=<root>  : %s"
                      % _("set the root directory") + '\n')
    sys.stderr.write( "\t-e, --export       : %s" 
                      % _("export list (default)") + '\n')
    sys.stderr.write("\t-i, --import       : %s" % _("import list") + '\n')
    sys.stderr.write( "\t-c, --clear        : %s" % 
          _("clear existing list prior of importing") + '\n')
    sys.stderr.write( "\t-f, --file=<file>  : %s" % 
          _("import from file") + '\n')
    sys.stderr.write('\n')

def main(mcmdline):
    from netconfpkg.NCDeviceList import getDeviceList
    from netconfpkg.NCHardwareList import getHardwareList               
    from netconfpkg.NCIPsecList import getIPsecList
    from netconfpkg.NCProfileList import getProfileList
    from netconfpkg.NC_functions import log

    signal.signal (signal.SIGINT, signal.SIG_DFL)
    class BadUsage(Exception):
        pass

    #progname = os.path.basename(sys.argv[0])
    NC_functions.setVerboseLevel(2)
    NC_functions.setDebugLevel(0)

    do_activate = 0
    switch_profile = 0
    profile = None
    test = 0
    EXPORT = 1
    IMPORT = 2
    SWITCH = 3
    mode = EXPORT
    filename = None
    clear = 0
    chroot = None
    debug = None
    devlists = []

    try:
        opts = getopt.getopt(mcmdline, "asp:?r:dhvtief:co",
                                   [
                                    "activate",
                                    "profile=",
                                    "help",
                                    "devicelist",
                                    "verbose",
                                    "test",
                                    "import",
                                    "export",
                                    "clear",
                                    "root=",
                                    "file=",
                                    "debug",
                                    "hardwarelist",
                                    "ipseclist",
                                    "profilelist"])[0]
        for opt, val in opts:
            if opt == '-r' or opt == '--root':                
                chroot = val
                NC_functions.prepareRoot(chroot)
                NC_functions.updateNetworkScripts()
                continue
    except (getopt.error, BadUsage):
        pass

    try:
        opts = getopt.getopt(mcmdline, "asp:?r:dhvtief:co",
                                   [
                                    "activate",
                                    "profile=",
                                    "help",
                                    "devicelist",
                                    "verbose",
                                    "test",
                                    "import",
                                    "export",
                                    "clear",
                                    "root=",
                                    "file=",
                                    "debug",
                                    "hardwarelist",
                                    "ipseclist",
                                    "profilelist"])[0]
        for opt, val in opts:
            if opt == '-d' or opt == '--devicelist':
                devlists.append(getDeviceList())
                continue

            if opt == '-h' or opt == '--hardwarelist':
                devlists.append(getHardwareList())
                continue

            if opt == '-s' or opt == '--ipseclist':
                devlists.append(getIPsecList())
                continue

            if opt == '-o' or opt == '--profilelist':
                devlists.append(getProfileList())
                continue

            if opt == '-p' or opt == '--profile':
                mode = SWITCH
                switch_profile = 1
                profile = val
                continue

            if opt == '-f' or opt == '--file':
                filename = val
                continue

            if opt == '-r' or opt == '--root':
                # already parsed
                continue

            if opt == '-c' or opt == '--clear':
                clear = 1
                continue

            if opt == '-t' or opt == '--test':
                test = 1
                continue

            if opt == '-a' or opt == '--activate':
                mode = SWITCH
                do_activate = 1
                continue

            if opt == '-i' or opt == '--import':
                mode = IMPORT
                continue

            if opt == '-e' or opt == '--export':
                mode = EXPORT
                continue

            if opt == '-?' or opt == '--help':
                Usage()
                return(0)

            if opt == '-v' or opt == '--verbose':
                NC_functions.setVerboseLevel(NC_functions.getVerboseLevel()+1)
                continue

            if opt == '--debug':
                NC_functions.setDebugLevel(NC_functions.getDebugLevel()+1)
                debug = 1
                continue

            sys.stderr.write(_("Unknown option %s\n" % opt))
            raise BadUsage

    except (getopt.error, BadUsage):
        Usage()
        return(1)

    try:

        if not NC_functions.getDebugLevel():
            log.handler = log.syslog_handler
            log.open()
        else:
            log.handler = log.file_handler
            log.open(sys.stderr)

        if not len(devlists):
            devlists = [getDeviceList(), getHardwareList(),
                        getIPsecList(),
                        getProfileList()]

        if clear:
            for devlist in devlists:
                del devlist[0:len(devlist)]

        if mode == EXPORT:
            for devlist in devlists:
                devstr =  str(devlist)
                if len(devstr):
                    # remove the last \n
                    print devstr[:-1]
            return(0)

        elif mode == IMPORT:
            devlistsdict = {
                "HardwareList" : getHardwareList(),
                "DeviceList" : getDeviceList(),
                "IPsecList" : getIPsecList(),
                "ProfileList" : getProfileList() }

            if filename:
                mfile = open(filename, "r")
            else:
                mfile = sys.stdin

            lines = mfile.readlines()

            for line in lines:
                try:
                    line = line[:-1]
                    log.log(3, "Parsing '%s'\n" % line)
                    vals = line.split("=")
                    if len(vals) <= 1:
                        continue
                    key = vals[0]
                    value = "=".join(vals[1:])

                    vals = key.split(".")
                    if devlistsdict.has_key(vals[0]):
                        # pylint: disable-msg=W0212
                        devlistsdict[vals[0]].fromstr(vals, value)
                    else:
                        sys.stderr.write(_("Unknown List %s\n", vals[0]))
                        raise ParseError

                except Exception, e:
                    pe = ParseError(_("Error parsing line: %s") % line)
                    pe.args += e.args
                    raise pe


            for devlist in devlists:
                log.log(1, "%s" % devlist)
                devlist.save()

            return(0)

        elif test:
            return(0)

        elif mode == SWITCH:
            ret = None
            profilelist = getProfileList()
            actdev = Control.NetworkDevice()
            actdev.load()
            aprof = profilelist.getActiveProfile()

            if switch_profile and aprof.ProfileName != profile:
                log.log(1, "Switching to profile %s" % profile)
                if do_activate:
                    for p in profilelist:
                        if p.ProfileName == profile:
                            aprof = p
                            break
                    for device in getDeviceList():
                        if device.DeviceId not in aprof.ActiveDevices:
                            if actdev.find(device.Device):
                                (ret, msg) = device.deactivate()
                                if ret:
                                    print msg
                profilelist.switchToProfile(profile)
                profilelist.save()

            actdev.load()

            if do_activate:
                aprof = profilelist.getActiveProfile()
                for device in getDeviceList():
                    if device.DeviceId in aprof.ActiveDevices:
                        if not actdev.find(device.Device) and \
                           device.OnBoot:
                            (ret, msg) = device.activate()
                            if ret:
                                print msg

                return(0)

        return(0)
    except SystemExit, code:
        #print "Exception %s: %s" % (str(SystemExit), str(code))
        return(code)
    except:
        handleException(sys.exc_info(), PROGNAME, PRG_VERSION, debug = debug)


if __name__ == '__main__':
    sys.exit(main(cmdline))

__author__ = "Harald Hoyer <harald@redhat.com>"
