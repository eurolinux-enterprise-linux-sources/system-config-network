#!/usr/bin/python
# -*- coding: utf-8 -*-

True = (1==1)
False = not True

import unittest
import sys
import string
import os


sys.path.append(os.getcwd() + "/../../")

if os.environ.has_key("srcdir"):
    srcdir = os.environ["srcdir"]
else:
    srcdir = os.getcwd()
sys.path.append(srcdir + "/../../")


CHROOT = os.path.abspath(os.getcwd()) + "/./rcntest-root"

BASICSETUP="""DeviceList.Ethernet.eth0.Type=Ethernet
DeviceList.Ethernet.eth0.BootProto=dhcp
DeviceList.Ethernet.eth0.Device=eth0
DeviceList.Ethernet.eth0.OnBoot=True
DeviceList.Ethernet.eth0.DeviceId=eth0
ProfileList.default.ActiveDevices.1=eth0
ProfileList.default.HostsList.1.IP=127.0.0.1
ProfileList.default.HostsList.1.Hostname=localhost.localdomain
ProfileList.default.HostsList.1.AliasList.1=localhost
ProfileList.default.HostsList.1.AliasList.2=localhost
ProfileList.default.DNS.SecondaryDNS=172.16.2.15
ProfileList.default.DNS.SearchList.1=stuttgart.redhat.com
ProfileList.default.DNS.SearchList.2=devel.redhat.com
ProfileList.default.DNS.SearchList.3=redhat.com
ProfileList.default.DNS.Domainname=
ProfileList.default.DNS.Hostname=jever.stuttgart.redhat.com
ProfileList.default.DNS.TertiaryDNS=
ProfileList.default.DNS.PrimaryDNS=172.16.2.2
ProfileList.default.Active=True
ProfileList.default.ProfileName=default
"""

def writeConf(filename, str):
    try: os.unlink(filename)
    except OSError: pass
    file = open(filename, 'w+', -1)
    file.write(str)
    file.close()

def sortStr(str):
    str = string.split(str, '\n')
    str.sort()
    #str = string.join(str, '\n')
    while str[0] == "":
        str = str[1:]
    return str


def expectConf(fileorlines, str):
    if os.path.isfile(fileorlines):
        file = open(fileorlines, 'r', -1)
        lines = file.readlines()
        lines.sort()
        for i in xrange(len(lines)):
            if lines[i][-1:] == "\n":
                lines[i] = lines[i][:-1]

    else:
        lines = sortStr(fileorlines)

    str = string.split(str, '\n')
    str.sort()
    #str = string.join(str, '\n')
    if str[0] == "":
        str = str[1:]

    l = min(len(lines), len(str))

    for i in xrange(l):
        if (lines[i] != str[i]):
            print "\n- %s\n+ %s\n" % (str[i], lines[i])
            break
    else:
        return True

    print lines
    return False



class TestGUI(unittest.TestCase):
    def setupChroot(self):
        cmd = "[ -d '%s' ] && rm -fr '%s'" % (CHROOT, CHROOT)
        os.system(cmd)
        cmd = "cp -ar '%s/test-root' '%s';chmod -R ug+rw %s" % (srcdir, CHROOT, CHROOT)
        os.system(cmd)

    def setUp(self):
        self.oldstderr = sys.stderr
        self.oldstdout = sys.stdout
        self.setupChroot()

    def tearDown(self):
        sys.stderr = self.oldstderr
        sys.stdout = self.oldstdout
        os.system("rm -fr '%s'" % CHROOT)

    def test00Basic(self):
        """Run the GUI and click Quit"""
        exedir = srcdir + "/../../"
        os.system("echo %s;cd %s;./netconf.py -d -r %s" % (exedir, exedir, CHROOT))

def suite():
    suite = unittest.TestSuite()
    suite = unittest.makeSuite(TestGUI, 'test')
    return suite

if __name__ == "__main__":
    docoverage = False
    #docoverage = True
    if docoverage:
        import coverage
        coverage.erase()
        coverage.start()
    import netconfpkg
    testRunner = unittest.TextTestRunner(verbosity=2)
    result = testRunner.run(suite())
    if docoverage:
        coverage.stop()
        m = []
        keys = []
        keys.extend(sys.modules.keys())
        keys.sort()
        for key in keys:
            try:
                path = sys.modules[key].__file__
            except:
                path = ""
            if path.find(".py") == -1:
                continue
            if key.find("netconfpkg") != -1:
                m.append(sys.modules[key])
            elif key.find("rhpl") != -1:
                m.append(sys.modules[key])

        coverage.the_coverage.report(m, show_missing=0 )
        coverage.the_coverage.annotate(m, os.getcwd())

    sys.exit(not result.wasSuccessful())

__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/03/14 09:29:37 $"
__version__ = "$Revision: 1.4 $"
