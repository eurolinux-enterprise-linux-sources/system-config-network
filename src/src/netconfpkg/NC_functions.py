## Copyright (C) 2001-2006 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2006 Harald Hoyer <harald@redhat.com>
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

# pylint: disable-msg=W0603
import __builtin__
import sys

import locale
import gettext
import os.path
import re
import shutil
from netconfpkg.conf import ConfShellVar, ConfPAP
from netconfpkg.log import LogFile
import ethtool

PROGNAME = "system-config-network"

log = LogFile(PROGNAME)

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
__builtin__.__dict__['_'] = _

_kernel_version = None

def kernel_version():
    global _kernel_version
    if not _kernel_version:
        (sysname, nodename, 
         release, version, machine) = os.uname() # pylint: disable-msg=W0612
        if release.find("-") != -1:
            (ver, rel) = release.split("-", 1) # pylint: disable-msg=W0612
        else:
            ver = release
        _kernel_version = ver.split(".", 4)
    return _kernel_version

def cmp_kernel_version(v1, v2):
    for i in (1, 2, 3):
        if v1[i] != v2[i]:
            try:
                return int(v1[i]) - int(v2[i])
            except:
                if (v1[i] > v2[i]):
                    return 1
                else:
                    return -1
    return 0


NETCONFDIR = '/usr/share/system-config-network/'
OLDSYSCONFDEVICEDIR = '/etc/sysconfig/network-scripts/'
SYSCONFNETWORKING = '/etc/sysconfig/networking/'
SYSCONFDEVICEDIR = SYSCONFNETWORKING + 'devices/'
SYSCONFPROFILEDIR = SYSCONFNETWORKING + 'profiles/'
SYSCONFNETWORK = '/etc/sysconfig/network'
WVDIALCONF = '/etc/wvdial.conf'
HOSTSCONF = '/etc/hosts'
RESOLVCONF = '/etc/resolv.conf'
PPPDIR = "/etc/ppp"

if cmp_kernel_version([2, 5, 0], kernel_version()) < 0:
    MODULESCONF = '/etc/modprobe.d/network.conf'
else:
    MODULESCONF = '/etc/modules.conf'

HWCONF = '/etc/sysconfig/hwconf'
ISDNCARDCONF = '/etc/sysconfig/isdncard'
PAPFILE = "/etc/ppp/pap-secrets"
CHAPFILE = "/etc/ppp/chap-secrets"

DEFAULT_PROFILE_NAME = _("Common")

ETHERNET = 'Ethernet'
MODEM = 'Modem'
ISDN = 'ISDN'
LO = 'Loopback'
DSL = 'xDSL'
WIRELESS = 'Wireless'
TOKENRING = 'TokenRing'
IPSEC = 'IPSEC'
QETH = 'QETH'
HSI = 'HSI'

deviceTypes = [ ETHERNET, MODEM, ISDN, LO, DSL, WIRELESS, TOKENRING, QETH, HSI ]

modemDeviceList = [ '/dev/modem', 
                    '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', '/dev/ttyS3', 
                    '/dev/ttyI0', '/dev/ttyI1', '/dev/ttyI2', '/dev/ttyI3', 
                    '/dev/input/ttyACM0', '/dev/input/ttyACM1', 
                    '/dev/input/ttyACM2', '/dev/input/ttyACM3', 
                    '/dev/ttyM0', '/dev/ttyM1' ]

__deviceTypeDict = { '^eth[0-9]*(:[0-9]+)?$' : ETHERNET, 
                     '^ppp[0-9]*(:[0-9]+)?$' : MODEM, 
                     '^ippp[0-9]*(:[0-9]+)?$' : ISDN, 
                     '^isdn[0-9]*(:[0-9]+)?$' : ISDN, 
                     '^tr[0-9]*(:[0-9]+)?$' :TOKENRING, 
                     '^lo$' : LO, 
                     '^hsi[0-9]*(:[0-9]+)?$' : HSI, 
                     '^wlan[0-9]*(:[0-9]+)?$' : WIRELESS, 
                     }

# Removed for now, until we have a config dialog for infrared
#                  '^irlan[0-9]+(:[0-9]+)?$' : WIRELESS


ACTIVE = _('Active')
INACTIVE = _('Inactive')


CRTSCTS = "CRTSCTS"
XONXOFF = "XONXOFF"
NOFLOW = "NOFLOW"

modemFlowControls = { CRTSCTS : _("Hardware (CRTSCTS)"), 
                      XONXOFF : _("Software (XON/XOFF)"), 
                      NOFLOW :  _("None") }


def nop(*args, **kwargs): # pylint: disable-msg=W0613
    pass

_testenv = False

def setTestEnv(val):
    global _testenv
    _testenv = val
    
def getTestEnv():
    return _testenv

_verbose = 0

def setVerboseLevel(l):
    global _verbose
    #print "Set verbose %d" % l
    log.set_loglevel(l)
    _verbose = l

def getVerboseLevel():
    return _verbose

_debug = 0

def setDebugLevel(l):
    global _debug
    #print "Set debug %d" % l
    _debug = l

def getDebugLevel():
    return _debug

class TestError(Exception):
    def __init__(self, args=None):
        Exception.__init__(self, args)
        #self.args = args

def gen_hexkey(mlen = 16):
    import struct
    key = ""
    f = file("/dev/random", "rb")
    chars = struct.unpack("%dB" % len, f.read(mlen))
    for i in chars:
        key = key + "%02x" % i
    f.close()
    return key

def rpms_notinstalled(namelist):
    if not namelist:
        return None
    try:
        import rpm

        ts = rpm.TransactionSet("/")
        ts.setVSFlags(rpm.RPMVSF_NORSA|rpm.RPMVSF_NODSA)
        ts.setFlags(rpm.RPMTRANS_FLAG_NOMD5)

        if len(namelist) == 0:
            namelist = [ namelist ]

        toinstall = namelist[:]

        for name in namelist:
            mi = ts.dbMatch('name', name)
            for n in mi:
                #print n[rpm.RPMTAG_NAME]
                if n[rpm.RPMTAG_NAME] == name:
                    toinstall.remove(name)
                    break

        del (ts)
        return toinstall
    except:
        return None

def assure_rpms(pkgs = None):
    toinstall = rpms_notinstalled(pkgs)

    r = RESPONSE_NO
    if toinstall and len(toinstall):
        plist = '\n'.join(toinstall)
        r = generic_longinfo_dialog(_("Shall the following packages, "
                                      "which are needed on your system, "
                                      "be installed?"), 
                                    plist, dialog_type="question")
        return r
    return r

def request_rpms(pkgs = None):
    toinstall = rpms_notinstalled(pkgs)

    if toinstall and len(toinstall):
        plist = "\n".join(toinstall)
        generic_longinfo_dialog(_("You have to install the following packages, "
                                  "which are needed on your system!"), 
                                  plist, dialog_type="info")
        return 1
    return 0

# we want to compile the regexp just once (not as fast as I expect)
ip_pattern = re.compile('^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$')
hostname_pattern = re.compile('^([a-zA-Z]|[0-9]|_)(([a-zA-Z]|[0-9]|-|_)*([a-zA-Z]|[0-9]|_))?(\.([a-zA-Z]|[0-9]|_)(([a-zA-Z]|[0-9]|-|_)*([a-zA-Z]|[0-9]))?)*$')
length_pattern = re.compile('^[a-zA-Z0-9-_]{1,64}(\.([a-zA-Z0-9-_]{1,64}))*$')
def testHostname(hostname):
    # hostname: names separated by '.' every name must be max 63 
    # chars in length and the hostname max length is 255 chars
    if not hostname:
        return False
    if (len(hostname)) < 256:
        # according to RFC 952 <name>  ::= <let>[*[<let-or-digit-or-hyphen>]<let-or-digit>]
        # & RFC 1123 - allows trailing and starting digits
        # ip like hostname are not allowed
        if ip_pattern.match(hostname):
            return False
        if not length_pattern.match(hostname):
            return False
        if not hostname_pattern.match(hostname):
            return False
        return True

def netmask_to_bits(netmask):
    vals = netmask.split(".")
    if len(vals) == 4:
        netmask = 0
        for val in vals:
            netmask *= 256
            try: 
                netmask += long(val)
            except: 
                pass
    else:
        return 0

    bits = 0
    while netmask:
        if netmask & 1: 
            bits += 1
        netmask = netmask >> 1

    return bits

def bits_to_netmask(bits):
    try:
        bits = int(bits)
    except:
        return ""

    rem = 32 - bits
    netmask = long(0)

    while bits:
        netmask = netmask << 1
        netmask = netmask | 1
        bits -= 1

    while rem:
        netmask = netmask << 1
        rem -= 1

    netstr = str(netmask >> 24) + "." + \
             str(netmask >> 16 & 255) + "." + \
             str(netmask >> 8 & 255) + "." + \
             str(netmask & 255)

    return netstr

DVpapconf = None
def getPAPConf():
    global DVpapconf
    if DVpapconf == None or DVpapconf.filename != getRoot() + PAPFILE:
        # FIXME: [197781] catch exceptions
        DVpapconf = ConfPAP.ConfPAP(getRoot() + PAPFILE)
    return DVpapconf

DVchapconf = None
def getCHAPConf():
    global DVchapconf
    if DVchapconf == None or DVchapconf.filename != getRoot() + CHAPFILE:
        # FIXME: [197781] catch exceptions
        DVchapconf = ConfPAP.ConfPAP(getRoot() + CHAPFILE)
    return DVchapconf


def create_combo(hardwarelist, devname, mtype, default_devices):
    hwdesc = default_devices
    hwcurr = None

    for hw in hardwarelist:
        if hw.Type == mtype and not getattr(hw, "Master", None):
            desc = str(hw.Name)
            if hw.Description:
                desc += ' (' + hw.Description + ')'
            try:
                i = hwdesc.index(hw.Name)
                hwdesc[i] = desc
            except:
                hwdesc.append(desc)

            if devname and hw.Name == devname:
                hwcurr = desc

    if not hwcurr:
        if devname:
            hwcurr = devname
        elif len(hwdesc):
            hwcurr = hwdesc[0]

    hwdesc.sort()

    return (hwcurr, hwdesc[:])

def create_generic_combo(hardwarelist, devname, mtype = ETHERNET, new = None):
    devbase = re.sub('[0-9]*(:[0-9]+)?$', '', devname)
    hwdesc = []
    for i in xrange(0, 9):
        hwdesc.append(devbase + str(i))

    if not new:
        return create_combo(hardwarelist, devname, mtype, 
                            default_devices = hwdesc)
    else:
        return (None, hwdesc)


def create_ethernet_combo(hardwarelist, devname, mtype = ETHERNET):
    hwdesc = [ 'eth0', 'eth1', 'eth2', 
               'eth3', 'eth4', 'eth5', 
               'eth6', 'eth7', 'eth8'
               ]

    return create_combo(hardwarelist, devname, mtype, 
                        default_devices = hwdesc)

def create_tokenring_combo(hardwarelist, devname):
    hwdesc = [ 'tr0', 'tr1', 'tr2', 
               'tr3', 'tr4', 'tr5', 
               'tr6', 'tr7', 'tr8'
               ]
    return create_combo(hardwarelist, devname, mtype = TOKENRING, 
                        default_devices = hwdesc)

def ishardlink(mfile):
    if os.path.isfile(mfile):
        return os.stat(mfile)[3] > 1
    else:
        return None

def issamefile(file1, file2):
    try:
        s1 = os.stat(file1)
        s2 = os.stat(file2)
    except:
        return False
    return os.path.samestat(s1, s2)

def getHardwareType(devname):
    if devname in deviceTypes:
        return devname
    return getDeviceType(devname)

def getDeviceType(devname, module = None):    
    if devname in deviceTypes:
        return devname

    if module == "qeth":
        return QETH

    UNKNOWN = _('Unknown')

    mtype = UNKNOWN

    if not devname or devname == "":
        return mtype

    for i in __deviceTypeDict.keys():
        if re.search(i, devname):
            mtype = __deviceTypeDict[i]

    if mtype == UNKNOWN:
        try:
            # if still unknown, try to get a MAC address
            hwaddr = ethtool.get_hwaddr(devname)
            if hwaddr:
                mtype = ETHERNET
        except:
            pass

    if mtype == ETHERNET:
        try:
            import iwlib
            # test for wireless
            iwlib.get_iwconfig(devname)
            mtype = WIRELESS
        except:
            pass

    return mtype

def getNickName(devicelist, dev):
    nickname = []
    for d in devicelist:
        if d.Device == dev:
            nickname.append(d.DeviceId)
    return nickname

def getNewDialupDevice(devicelist, dev):
    dlist = []
    count = 0
    device = None

    for i in devicelist:
        if dev.Device != i.Device:
            dlist.append(i.Device)
            if (i.Type == ISDN 
                and i.Dialup.EncapMode == 'syncppp' 
                and i.Dialup.ChannelBundling):
                dlist.append(i.Dialup.SlaveDevice)
        else:
            if (i.Type == ISDN 
                and i.Dialup.EncapMode == 'syncppp' 
                and i.Dialup.ChannelBundling):
                dlist.append(i.Device)

    if dev.Type == ISDN:
        if dev.Dialup.EncapMode == 'syncppp':
            device = 'ippp'
        else:
            device = 'isdn'
    else:
        device = 'ppp'

    while 1:
        if device+str(count) in dlist:
            count = count + 1
        else:
            return device+str(count)

# Some failsafe return codes (same as in gtk)
RESPONSE_NONE = -1
RESPONSE_REJECT = -2
RESPONSE_ACCEPT = -3
RESPONSE_DELETE_EVENT = -4
RESPONSE_OK = -5
RESPONSE_CANCEL = -6
RESPONSE_CLOSE = -7
RESPONSE_YES = -8
RESPONSE_NO = -9
RESPONSE_APPLY = -10
RESPONSE_HELP = -11

# FIXME: replace "print message" with logging
generic_error_dialog_func = None
def generic_error_dialog (message, parent_dialog = None, dialog_type="warning", 
                          widget=None, page=0, broken_widget=None):
    if generic_error_dialog_func:
        return generic_error_dialog_func("%s:\n\n%s" % (PROGNAME, 
                                                        message), 
                                         parent_dialog, 
                                         dialog_type, widget, 
                                         page, broken_widget)
    else:
        print message
    return 0

generic_info_dialog_func = None
def generic_info_dialog (message, parent_dialog = None, dialog_type="info", 
                          widget=None, page=0, broken_widget=None):
    if generic_info_dialog_func:
        return generic_info_dialog_func("%s:\n\n%s" % (PROGNAME, 
                                                       message), 
                                        parent_dialog, 
                                        dialog_type, widget, 
                                        page, broken_widget)
    else:
        print message
    return 0

generic_longinfo_dialog_func = None
def generic_longinfo_dialog (message, long_message, 
                             parent_dialog = None, dialog_type="info", 
                             widget=None, page=0, broken_widget=None):
    if generic_longinfo_dialog_func:
        return generic_longinfo_dialog_func("%s:\n\n%s" % (PROGNAME, 
                                                           message), 
                                            long_message, 
                                            parent_dialog, 
                                            dialog_type, widget, 
                                            page, broken_widget)
    else:
        print message
    return 0

generic_yesnocancel_dialog_func = None
def generic_yesnocancel_dialog (message, parent_dialog = None, 
                                dialog_type="question", 
                                widget=None, page=0, broken_widget=None):
    if generic_yesnocancel_dialog_func:
        return generic_yesnocancel_dialog_func("%s:\n\n%s" % (PROGNAME, 
                                                              message), 
                                               parent_dialog, 
                                               dialog_type, widget, 
                                               page, broken_widget)
    else:
        print message
    return 0

generic_yesno_dialog_func = None
def generic_yesno_dialog (message, parent_dialog = None, 
                          dialog_type="question", 
                          widget=None, page=0, broken_widget=None):
    if generic_yesno_dialog_func:
        return generic_yesno_dialog_func("%s:\n\n%s" % (PROGNAME, 
                                                        message), 
                                         parent_dialog, 
                                         dialog_type, widget, 
                                         page, broken_widget)
    else:
        print message
    return 0

generic_run_dialog_func = None
def generic_run_dialog (command, argv, searchPath = 0, 
                        root = '/', stdin = 0, 
                        catchfd = 1, closefd = -1, title = None, 
                        label = None, errlabel = None, dialog = None):
    import select
    if generic_run_dialog_func:
        return generic_run_dialog_func(command, argv, searchPath, 
                                       root, stdin, catchfd, 
                                       title = "%s:\n\n%s" % (PROGNAME, 
                                                              title), 
                                       label = label, 
                                       errlabel = errlabel, 
                                       dialog = dialog)
    else:
        if not os.access (root + command, os.X_OK):
            raise RuntimeError, command + " can not be run"

        print title
        print label

        log.log(1, "Running %s %s" % (command, " ".join(argv)))
        (read, write) = os.pipe()

        childpid = os.fork()
        if (not childpid):
            if (root and root != '/'): 
                os.chroot (root)
            if isinstance(catchfd, tuple):
                for fd in catchfd:
                    os.dup2(write, fd)
            else:
                os.dup2(write, catchfd)
            os.close(write)
            os.close(read)

            if closefd != -1:
                os.close(closefd)

            if stdin:
                os.dup2(stdin, 0)
                os.close(stdin)

            if (searchPath):
                os.execvp(command, argv)
            else:
                os.execv(command, argv)

            sys.exit(1)
        try:
            os.close(write)

            rc = ""
            s = "1"
            while (s):
                try:
                    # pylint: disable-msg=W0612
                    (fdin, fdout, fderr) = select.select([read], [], [], 0.1)
                except:
                    fdin = []

                if len(fdin):
                    s = os.read(read, 100)
                    sys.stdout.write(s)
                    rc = rc + s

        except Exception, e:
            try:
                os.kill(childpid, 15)
            except:
                pass
            raise e

        os.close(read)

        try:
            # pylint: disable-msg=W0612
            (pid, status) = os.waitpid(childpid, 0)
        except OSError, (errno, msg):
            #print __name__, "waitpid:", msg
            pass

        if os.WIFEXITED(status) and (os.WEXITSTATUS(status) == 0):
            status = os.WEXITSTATUS(status)
        else:
            status = -1

        return (status, rc)

generic_run_func = None
def generic_run (command, argv, searchPath = 0, 
                 root = '/', stdin = 0, 
                 catchfd = 1, closefd = -1):
    import select
    if generic_run_func:
        return generic_run_func(command, argv, searchPath, 
                                       root, stdin, catchfd)
    else:
        if not os.access (root + command, os.X_OK):
            raise RuntimeError, command + " can not be run"

        log.log(1, "Running %s %s" % (command, argv.join()))
        (read, write) = os.pipe()

        childpid = os.fork()
        if (not childpid):
            if (root and root != '/'): 
                os.chroot (root)
            if isinstance(catchfd, tuple):
                for fd in catchfd:
                    os.dup2(write, fd)
            else:
                os.dup2(write, catchfd)
            os.close(write)
            os.close(read)

            if closefd != -1:
                os.close(closefd)

            if stdin:
                os.dup2(stdin, 0)
                os.close(stdin)

            if (searchPath):
                os.execvp(command, argv)
            else:
                os.execv(command, argv)

            sys.exit(1)
        try:
            os.close(write)

            rc = ""
            s = "1"
            while (s):
                try:
                    # pylint: disable-msg=W0612
                    (fdin, fdout, fderr) = select.select([read], 
                                                         [], [], 0.1)
                except:
                    fdin = []

                if len(fdin):
                    s = os.read(read, 100)
                    sys.stdout.write(s)
                    rc = rc + s

        except Exception, e:
            try:
                os.kill(childpid, 15)
            except:
                pass
            raise e

        os.close(read)

        try:
            # pylint: disable-msg=W0612
            (pid, status) = os.waitpid(childpid, 0)
        except OSError, (errno, msg):
            #print __name__, "waitpid:", msg
            pass

        if os.WIFEXITED(status) and (os.WEXITSTATUS(status) == 0):
            status = os.WEXITSTATUS(status)
        else:
            status = -1

        return (status, rc)

def set_generic_error_dialog_func(func):
    global generic_error_dialog_func
    generic_error_dialog_func = func

def set_generic_info_dialog_func(func):
    global generic_info_dialog_func
    generic_info_dialog_func = func

def set_generic_longinfo_dialog_func(func):
    global generic_longinfo_dialog_func
    generic_longinfo_dialog_func = func

def set_generic_yesnocancel_dialog_func(func):
    global generic_yesnocancel_dialog_func
    generic_yesnocancel_dialog_func = func

def set_generic_yesno_dialog_func(func):
    global generic_yesno_dialog_func
    generic_yesno_dialog_func = func

def set_generic_run_dialog_func(func):
    global generic_run_dialog_func
    generic_run_dialog_func = func

def set_generic_run_func(func):
    global generic_run_func
    generic_run_func = func


def unlink(mfile):
    if not (os.path.isfile(mfile) or os.path.islink(mfile)):
            #print "file '%s' is not a file!" % file
        return
    try:
        os.unlink(mfile)
        log.log(2, "rm %s" % mfile)
    except OSError, errstr:
        generic_error_dialog (_("Error removing\n%s:\n%s!") \
                              % (mfile, str(errstr)))

def rmdir(mfile):
    if not os.path.isdir(mfile):
    #print "file '%s' is not a file!" % file
        return
    try:
        os.rmdir(mfile)
        log.log(2, "rmdir %s" % mfile)
    except OSError, errstr:
        generic_error_dialog (_("Error removing\n%s:\n%s!") \
                              % (mfile, str(errstr)))

def link(src, dst):
    if not os.path.isfile(src):
        return
    try:
        os.link(src, dst)
        # restore selinux context
        try:
            os.system("/sbin/restorecon %s >/dev/null 2>&1" % dst)
        except:
            pass
        log.log(2, "ln %s %s" % (src, dst))
    except:
        symlink(src, dst)

def copy(src, dst):
    if not os.path.isfile(src):
        return
    try:
        shutil.copy(src, dst)
        shutil.copymode(src, dst)
        try:
            os.system("/sbin/restorecon %s >/dev/null 2>&1" % dst)
        except:
            pass
        log.log(2, "cp %s %s" % (src, dst))
    except (IOError, OSError), errstr:
        generic_error_dialog (_("Error copying \n%s\nto %s:\n%s!")
                              % (src, dst, str(errstr)))

def symlink(src, dst):
    if not os.path.isfile(src):
        return
    try:
        os.symlink(src, dst)
        log.log(2, "ln -s %s %s" % (src, dst))
    except OSError, errstr:
        generic_error_dialog (_("Error linking \n%s\nto %s:\n%s!")
                              % (src, dst, str(errstr)))

def rename(src, dst):
    if not os.path.isfile(src) and not os.path.isdir(src):
        return
    try:
        os.rename(src, dst)
        log.log(2, "mv %s %s" % (src, dst))
    except (IOError, OSError, EnvironmentError), errstr:
        generic_error_dialog (_("Error renaming \n%s\nto %s:\n%s!") \
                              % (src, dst, str(errstr)))

def mkdir(path):
    try:
        os.mkdir(path)
        log.log(2, "mkdir %s" % path)
    except (IOError, OSError), errstr :
        generic_error_dialog (_("Error creating directory!\n%s") \
                              % (str(errstr)))

    try:
        os.system("/sbin/restorecon %s >/dev/null 2>&1" % path)
    except:
        pass


def get_filepath(mfile):
    fn = mfile
    if not os.path.exists(fn):
        fn = NETCONFDIR + file
    else: 
        return fn

    if not os.path.exists(fn):
        return None
    else:
        return fn

class ConfDevices(list):
    def __init__(self, confdir = None):
        list.__init__(self)
        if confdir == None:
            confdir = getRoot() + SYSCONFDEVICEDIR
        confdir += '/'
        try:
            mdir = os.listdir(confdir)
        except OSError:
            pass
        else:
            # FIXME: handle ifcfg-${parent_device}-range* rhbz#221292
            for entry in mdir:
                if (len(entry) > 6) and \
                   entry[:6] == 'ifcfg-' and \
                   os.path.isfile(confdir + entry) and \
                   (confdir + entry)[-1] != "~" and \
                   entry.find('.rpmsave') == -1 and \
                   entry.find('.rpmnew') == -1 and \
                   entry.find('-range') == -1 and \
                   os.access(confdir + entry, os.R_OK):
                    self.append(entry[6:])
        self.sort()

def testFilename(filename):
    if not len(filename):
        return False

    if (not os.access(filename, os.R_OK)) or \
           (not os.path.isfile(filename)) or \
           (os.path.islink(filename)):
        return False

    if filename[-1] == "~":
        return False

    if len(filename) > 7 and filename[:7] == '.rpmnew':
        return False

    if len(filename) > 8 and filename[:8] == '.rpmsave':
        return False

    if len(filename) > 8 and filename[:8] == '.rpmorig':
        return False

    return True

__root = "/"

def setRoot(root):
    global __root
    __root = root

def getRoot():
    return __root

def prepareRoot(root):
    log.log(5, "prepareRoot()")
    setRoot(root)

    for mdir in "/etc", "/etc/sysconfig", \
        SYSCONFNETWORKING, \
        OLDSYSCONFDEVICEDIR, \
        SYSCONFDEVICEDIR, \
        SYSCONFPROFILEDIR, \
        PPPDIR:
        if not os.path.isdir(root + "/" + mdir):
            mkdir(root + "/" + mdir)


class ConfKeys(ConfShellVar.ConfShellVar):
    def __init__(self, name):
        ConfShellVar.ConfShellVar.__init__(self, 
                                           getRoot() 
                                           + SYSCONFDEVICEDIR 
                                           + 'keys-' + name)
        self.chmod(0600)


__updatedNetworkScripts = False

def updateNetworkScripts(force = False):
    global __updatedNetworkScripts

    log.log(5, "updateNetworkScripts()")

    if __updatedNetworkScripts and (not force):
        return 

    if not os.access(getRoot() + "/", os.W_OK):
        log.log(5, "Cannot write to %s" % (getRoot() + "/"))
        return

    prepareRoot(getRoot())

    firsttime = False

    if not os.path.isdir(getRoot() + SYSCONFPROFILEDIR+'/default/'):
        firsttime = True
        mkdir(getRoot() + SYSCONFPROFILEDIR+'/default')

    curr_prof = 'default'
    if not firsttime:
        # FIXME: [197781] catch exceptions
        nwconf = ConfShellVar.ConfShellVar(getRoot() + SYSCONFNETWORK)
        if nwconf.has_key('CURRENT_PROFILE'):
            curr_prof = nwconf['CURRENT_PROFILE']

    # FIXME: [197781] catch exceptions
    devlist = ConfDevices(getRoot() + OLDSYSCONFDEVICEDIR)

    for dev in devlist:
        if dev == 'lo':
            continue

        ocfile = getRoot() + OLDSYSCONFDEVICEDIR+'/ifcfg-'+ dev
        dfile = getRoot() + SYSCONFDEVICEDIR+'/ifcfg-'+dev

        if issamefile(ocfile, dfile):
            continue

        unlink(getRoot() + SYSCONFDEVICEDIR+'/ifcfg-'+dev)
        link(ocfile, dfile)

        log.log(1, _("Linking %s to devices and putting "
                     "it in profile %s.") % (dev, curr_prof))

        pfile = getRoot() + SYSCONFPROFILEDIR+'/' + curr_prof + '/ifcfg-'+dev

        unlink(pfile)
        link(dfile, pfile)

    for (mfile, cfile) in { RESOLVCONF : '/resolv.conf', 
                           HOSTSCONF : '/hosts' }.items():
        hostfile = getRoot() + mfile
        conffile = getRoot() + SYSCONFPROFILEDIR + '/' + \
            curr_prof + cfile
        if not os.path.isfile(conffile) or not issamefile(hostfile, conffile):
            unlink(conffile)
            link(hostfile, conffile)

    __updatedNetworkScripts = True

    return


__author__ = "Harald Hoyer <harald@redhat.com>"
