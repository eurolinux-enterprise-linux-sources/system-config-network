#!/usr/bin/python
# -*- coding: utf-8 -*-

True = (1==1)
False = not True

import unittest
import sys
import string
import os
import logging

sys.path.append(os.getcwd() + "/../../")

if os.environ.has_key("srcdir"):
    srcdir = os.environ["srcdir"]
    sys.path.append(srcdir + "/../../")
else:
    srcdir = os.getcwd()


CHROOT = os.path.abspath(os.getcwd()) + "/./rcntest-root"

BASICSETUP="""DeviceList.Ethernet.eth0.AllowUser=False
DeviceList.Ethernet.eth0.AutoDNS=True
DeviceList.Ethernet.eth0.BootProto=dhcp
DeviceList.Ethernet.eth0.Device=eth0
DeviceList.Ethernet.eth0.DeviceId=eth0
DeviceList.Ethernet.eth0.IPv6Init=False
DeviceList.Ethernet.eth0.NMControlled=False
DeviceList.Ethernet.eth0.OnBoot=True
DeviceList.Ethernet.eth0.Type=Ethernet
DeviceList.ISDN.1net4you0.AllowUser=True
DeviceList.ISDN.1net4you0.AutoDNS=True
DeviceList.ISDN.1net4you0.BootProto=dialup
DeviceList.ISDN.1net4you0.Device=ippp0
DeviceList.ISDN.1net4you0.DeviceId=1net4you0
DeviceList.ISDN.1net4you0.Dialup.Authentication=+pap -chap
DeviceList.ISDN.1net4you0.Dialup.ChannelBundling=False
DeviceList.ISDN.1net4you0.Dialup.Compression.AdressControl=False
DeviceList.ISDN.1net4you0.Dialup.Compression.BSD=False
DeviceList.ISDN.1net4you0.Dialup.Compression.CCP=False
DeviceList.ISDN.1net4you0.Dialup.Compression.ProtoField=False
DeviceList.ISDN.1net4you0.Dialup.Compression.VJID=False
DeviceList.ISDN.1net4you0.Dialup.Compression.VJTcpIp=False
DeviceList.ISDN.1net4you0.Dialup.DefRoute=True
DeviceList.ISDN.1net4you0.Dialup.DialMode=manual
DeviceList.ISDN.1net4you0.Dialup.EncapMode=syncppp
DeviceList.ISDN.1net4you0.Dialup.HangupTimeout=600
DeviceList.ISDN.1net4you0.Dialup.Login=web
DeviceList.ISDN.1net4you0.Dialup.Password=
DeviceList.ISDN.1net4you0.Dialup.Persist=False
DeviceList.ISDN.1net4you0.Dialup.PhoneNumber=019256252
DeviceList.ISDN.1net4you0.Dialup.ProviderName=1net4you
DeviceList.ISDN.1net4you0.Dialup.Secure=False
DeviceList.ISDN.1net4you0.IPv6Init=False
DeviceList.ISDN.1net4you0.OnBoot=False
DeviceList.ISDN.1net4you0.Type=ISDN
DeviceList.Modem.1net4you.AllowUser=True
DeviceList.Modem.1net4you.AutoDNS=True
DeviceList.Modem.1net4you.BootProto=dialup
DeviceList.Modem.1net4you.Device=ppp0
DeviceList.Modem.1net4you.DeviceId=1net4you
DeviceList.Modem.1net4you.Dialup.Compression.AdressControl=False
DeviceList.Modem.1net4you.Dialup.Compression.BSD=False
DeviceList.Modem.1net4you.Dialup.Compression.CCP=False
DeviceList.Modem.1net4you.Dialup.Compression.ProtoField=False
DeviceList.Modem.1net4you.Dialup.Compression.VJID=False
DeviceList.Modem.1net4you.Dialup.Compression.VJTcpIp=False
DeviceList.Modem.1net4you.Dialup.DefRoute=True
DeviceList.Modem.1net4you.Dialup.DialMode=manual
DeviceList.Modem.1net4you.Dialup.Inherits=Modem0
DeviceList.Modem.1net4you.Dialup.HangupTimeout=600
DeviceList.Modem.1net4you.Dialup.Login=web
DeviceList.Modem.1net4you.Dialup.Password=web
DeviceList.Modem.1net4you.Dialup.Persist=False
DeviceList.Modem.1net4you.Dialup.PhoneNumber=019256252
DeviceList.Modem.1net4you.Dialup.ProviderName=1net4you
DeviceList.Modem.1net4you.Dialup.StupidMode=True
DeviceList.Modem.1net4you.IPv6Init=False
DeviceList.Modem.1net4you.OnBoot=False
DeviceList.Modem.1net4you.Type=Modem
DeviceList.TokenRing.tr0.AllowUser=False
DeviceList.TokenRing.tr0.AutoDNS=True
DeviceList.TokenRing.tr0.BootProto=dhcp
DeviceList.TokenRing.tr0.Device=tr0
DeviceList.TokenRing.tr0.DeviceId=tr0
DeviceList.TokenRing.tr0.IPv6Init=False
DeviceList.TokenRing.tr0.OnBoot=True
DeviceList.TokenRing.tr0.Type=TokenRing
DeviceList.Wireless.eth3.AllowUser=False
DeviceList.Wireless.eth3.AutoDNS=True
DeviceList.Wireless.eth3.BootProto=dhcp
DeviceList.Wireless.eth3.Device=eth3
DeviceList.Wireless.eth3.DeviceId=eth3
DeviceList.Wireless.eth3.IPv6Init=False
DeviceList.Wireless.eth3.OnBoot=False
DeviceList.Wireless.eth3.Type=Wireless
DeviceList.Wireless.eth3.Wireless.Channel=1
DeviceList.Wireless.eth3.Wireless.EssId=
DeviceList.Wireless.eth3.Wireless.Key=
DeviceList.Wireless.eth3.Wireless.Mode=Auto
DeviceList.Wireless.eth3.Wireless.Rate=auto
HardwareList.Ethernet.eth0.Card.ModuleName=3c501
HardwareList.Ethernet.eth0.Description=3c501
HardwareList.Ethernet.eth0.Name=eth0
HardwareList.Ethernet.eth0.Status=configured
HardwareList.Ethernet.eth0.Type=Ethernet
HardwareList.Ethernet.eth1.Card.ModuleName=3c501
HardwareList.Ethernet.eth1.Description=3c501
HardwareList.Ethernet.eth1.Name=eth1
HardwareList.Ethernet.eth1.Status=configured
HardwareList.Ethernet.eth1.Type=Ethernet
HardwareList.Ethernet.eth2.Card.ModuleName=3c501
HardwareList.Ethernet.eth2.Description=3c501
HardwareList.Ethernet.eth2.Name=eth2
HardwareList.Ethernet.eth2.Status=configured
HardwareList.Ethernet.eth2.Type=Ethernet
HardwareList.Ethernet.eth3.Card.ModuleName=3c501
HardwareList.Ethernet.eth3.Description=3c501
HardwareList.Ethernet.eth3.Name=eth3
HardwareList.Ethernet.eth3.Status=configured
HardwareList.Ethernet.eth3.Type=Ethernet
HardwareList.ISDN.ISDN Card 0.Card.ChannelProtocol=2
HardwareList.ISDN.ISDN Card 0.Card.DeviceId=
HardwareList.ISDN.ISDN Card 0.Card.DriverId=HiSax
HardwareList.ISDN.ISDN Card 0.Card.Firmware=
HardwareList.ISDN.ISDN Card 0.Card.IRQ=5
HardwareList.ISDN.ISDN Card 0.Card.IoPort1=
HardwareList.ISDN.ISDN Card 0.Card.IoPort2=
HardwareList.ISDN.ISDN Card 0.Card.IoPort=0x300
HardwareList.ISDN.ISDN Card 0.Card.Mem=
HardwareList.ISDN.ISDN Card 0.Card.ModuleName=hisax
HardwareList.ISDN.ISDN Card 0.Card.Type=30
HardwareList.ISDN.ISDN Card 0.Card.VendorId=
HardwareList.ISDN.ISDN Card 0.Description=ACER P10
HardwareList.ISDN.ISDN Card 0.Name=ISDN Card 0
HardwareList.ISDN.ISDN Card 0.Status=configured
HardwareList.ISDN.ISDN Card 0.Type=ISDN
HardwareList.Modem.Modem0.Description=Generic Modem
HardwareList.Modem.Modem0.Modem.BaudRate=115200
HardwareList.Modem.Modem0.Modem.DeviceName=/dev/modem
HardwareList.Modem.Modem0.Modem.DialCommand=ATDT
HardwareList.Modem.Modem0.Modem.FlowControl=CRTSCTS
HardwareList.Modem.Modem0.Modem.InitString=ATZ
HardwareList.Modem.Modem0.Modem.ModemVolume=0
HardwareList.Modem.Modem0.Name=Modem0
HardwareList.Modem.Modem0.Status=configured
HardwareList.Modem.Modem0.Type=Modem
HardwareList.TokenRing.tr0.Card.ModuleName=olympic
HardwareList.TokenRing.tr0.Description=olympic
HardwareList.TokenRing.tr0.Name=tr0
HardwareList.TokenRing.tr0.Status=configured
HardwareList.TokenRing.tr0.Type=TokenRing
ProfileList.default.Active=True
ProfileList.default.ActiveDevices.1=1net4you
ProfileList.default.ActiveDevices.2=1net4you0
ProfileList.default.ActiveDevices.3=eth0
ProfileList.default.ActiveDevices.4=eth3
ProfileList.default.ActiveDevices.5=tr0
ProfileList.default.DNS.Domainname=
ProfileList.default.DNS.Hostname=test
ProfileList.default.DNS.PrimaryDNS=1.1.1.1
ProfileList.default.DNS.SearchList.1=home
ProfileList.default.DNS.SecondaryDNS=2.2.2.2
ProfileList.default.DNS.TertiaryDNS=3.3.3.3
ProfileList.default.HostsList.1.AliasList.1=localhost
ProfileList.default.HostsList.1.Hostname=localhost.localdomain
ProfileList.default.HostsList.1.IP=127.0.0.1
ProfileList.default.HostsList.2.AliasList.1=localhost6
ProfileList.default.HostsList.2.Hostname=localhost6.localdomain6
ProfileList.default.HostsList.2.IP=::1
ProfileList.default.HostsList.3.AliasList.1=test1
ProfileList.default.HostsList.3.AliasList.2=test2
ProfileList.default.HostsList.3.Hostname=test
ProfileList.default.HostsList.3.IP=10.1.1.1
ProfileList.default.ProfileName=default
"""

def writeConf(filename, str):
    try: os.unlink(filename)
    except OSError: pass
    file = open(filename, 'w+', -1)
    file.write(str)
    file.close()

def sortStr(mstr):
    mstr = mstr.split('\n')
    mstr.sort()
    while mstr[0] == "":
        mstr = mstr[1:]
    return mstr


def expectConf(fileorlines, mstr):
    if os.path.isfile(fileorlines):
        file = open(fileorlines, 'r', -1)
        lines = file.readlines()
        lines.sort()
        for i in xrange(len(lines)):
            if lines[i][-1:] == "\n":
                lines[i] = lines[i][:-1]

    else:
        lines = sortStr(fileorlines)


    mstr = sortStr(mstr)

    l = min(len(lines), len(mstr))

    for i in xrange(l):
        if (lines[i] != mstr[i]):
            file = open("stderr", 'r', -1)
            print >> sys.stderr
            print >> sys.stderr, "".join(file.readlines())
            file.close()
            
            print >> sys.stderr
            if i >= 2:
                print >> sys.stderr, "  %s" % (mstr[i-2])
            if i >= 1:
                print >> sys.stderr, "  %s" % (mstr[i-1])
            print >> sys.stderr, "- %s\n+ %s" % (mstr[i], lines[i])
            if (i+1) < l:
                print >> sys.stderr, "- %s\n+ %s" % (mstr[i+1], lines[i+1])
            if (i+2) < l:
                print >> sys.stderr, "- %s\n+ %s" % (mstr[i+2], lines[i+2])
            print
            break
    else:
        return True

    print "\n".join(lines)
    return False

class TestRCN(unittest.TestCase):
    def setupChroot(self):
        cmd = "[ -d '%s' ] && rm -fr '%s'" % (CHROOT, CHROOT)
        os.system(cmd)
        cmd = "cp -ar '%s/test-root' '%s';chmod -R ug+rw %s" % (srcdir, 
                                                                CHROOT, CHROOT)
        os.system(cmd)

    def setUp(self):
        self.oldstderr = sys.stderr
        self.oldstdout = sys.stdout

    def tearDown(self):
        sys.stderr = self.oldstderr
        sys.stdout = self.oldstdout
        try:
            #os.unlink("stderr")
            #os.unlink("stdout")
            pass
        except:
            pass

    def getConf(self):
        PROGNAME='system-config-network'
        import netconfpkg
        from netconfpkg import NC_functions
        NC_functions.prepareRoot(CHROOT)

        from netconfpkg import \
             NCDeviceList, NCProfileList, \
             NCHardwareList, NCIPsecList

        from netconfpkg.NC_functions import log

        NC_functions.setVerboseLevel(0)
        NC_functions.setDebugLevel(0)
        log.set_loglevel(NC_functions.getVerboseLevel())

        devlists = [
#            NCIPsecList.getIPsecList(),
            NCDeviceList.getDeviceList(),
            NCHardwareList.getHardwareList(),
            NCProfileList.getProfileList(),
            ]

        devstr = ""
        for devlist in devlists:
            devlist.load()
            devstr +=  str(devlist)
        return devstr

    def redirectStd(self):
        sys.stderr.flush()
        sys.stdout.flush()
        self.oldstderr = sys.stderr
        self.oldstdout = sys.stdout
        nout = open("stdout", "w")
        nerr = open("stderr", "w")
        from netconfpkg.NC_functions import log
        log.open(nerr)
        sys.stderr = nerr
        sys.stdout = nout

    def redirectEnd(self):
        from netconfpkg.NC_functions import log
        log.open(self.oldstderr)
        sys.stderr.close()
        sys.stdout.close()
        sys.stderr = self.oldstderr
        sys.stdout = self.oldstdout

    def test00Basic(self):
        """Testing basic reading from a chroot setup with network-cmd"""
        self.setupChroot()
        self.redirectStd()
        import netconf_cmd
        from netconfpkg.NC_functions import setTestEnv
        setTestEnv(True)
        cmdline = [ "-dh", "-o", "--root=" + CHROOT ]
        netconf_cmd.main(cmdline)
        expect = BASICSETUP
        self.redirectEnd()
        self.failUnless(expectConf("stdout", expect))

    def test01Read(self):
        """Test manual reading"""
        self.setupChroot()
        self.redirectStd()
        from netconfpkg import NC_functions
        NC_functions.prepareRoot(CHROOT)
        NC_functions.updateNetworkScripts(True)
        devstr = self.getConf()
        expect = BASICSETUP
        self.redirectEnd()
        self.failUnless(expectConf(expect, devstr))
   
    def test02Profile(self):
        """Test profile creation """
        #self.clearModules()
        self.setupChroot()
        self.redirectStd()
        from netconfpkg import NC_functions
        NC_functions.prepareRoot(CHROOT)
        NC_functions.updateNetworkScripts(True)

        from netconfpkg import NCProfileList
        from netconfpkg.NCProfile import Profile
        profilelist = NCProfileList.getProfileList()

        text = "newprofile"
        prof = Profile()
        profilelist.append(prof)
        prof.apply(profilelist[0])
        prof.ProfileName = text
        prof.commit()
        profilelist.switchToProfile(prof, dochange = True)
        self.save()

        devstr = self.getConf()
        expect = """DeviceList.Ethernet.eth0.AllowUser=False
DeviceList.Ethernet.eth0.AutoDNS=True
DeviceList.Ethernet.eth0.BootProto=dhcp
DeviceList.Ethernet.eth0.Device=eth0
DeviceList.Ethernet.eth0.DeviceId=eth0
DeviceList.Ethernet.eth0.IPv6Init=False
DeviceList.Ethernet.eth0.NMControlled=False
DeviceList.Ethernet.eth0.OnBoot=True
DeviceList.Ethernet.eth0.Type=Ethernet
DeviceList.ISDN.1net4you0.AllowUser=True
DeviceList.ISDN.1net4you0.AutoDNS=True
DeviceList.ISDN.1net4you0.BootProto=dialup
DeviceList.ISDN.1net4you0.Device=ippp0
DeviceList.ISDN.1net4you0.DeviceId=1net4you0
DeviceList.ISDN.1net4you0.Dialup.Authentication=+pap -chap
DeviceList.ISDN.1net4you0.Dialup.ChannelBundling=False
DeviceList.ISDN.1net4you0.Dialup.Compression.AdressControl=False
DeviceList.ISDN.1net4you0.Dialup.Compression.BSD=False
DeviceList.ISDN.1net4you0.Dialup.Compression.CCP=False
DeviceList.ISDN.1net4you0.Dialup.Compression.ProtoField=False
DeviceList.ISDN.1net4you0.Dialup.Compression.VJID=False
DeviceList.ISDN.1net4you0.Dialup.Compression.VJTcpIp=False
DeviceList.ISDN.1net4you0.Dialup.DefRoute=True
DeviceList.ISDN.1net4you0.Dialup.DialMode=manual
DeviceList.ISDN.1net4you0.Dialup.EncapMode=syncppp
DeviceList.ISDN.1net4you0.Dialup.HangupTimeout=600
DeviceList.ISDN.1net4you0.Dialup.Login=web
DeviceList.ISDN.1net4you0.Dialup.Password=
DeviceList.ISDN.1net4you0.Dialup.Persist=False
DeviceList.ISDN.1net4you0.Dialup.PhoneNumber=019256252
DeviceList.ISDN.1net4you0.Dialup.ProviderName=1net4you
DeviceList.ISDN.1net4you0.Dialup.Secure=False
DeviceList.ISDN.1net4you0.IPv6Init=False
DeviceList.ISDN.1net4you0.OnBoot=False
DeviceList.ISDN.1net4you0.Type=ISDN
DeviceList.Modem.1net4you.AllowUser=True
DeviceList.Modem.1net4you.AutoDNS=True
DeviceList.Modem.1net4you.BootProto=dialup
DeviceList.Modem.1net4you.Device=ppp0
DeviceList.Modem.1net4you.DeviceId=1net4you
DeviceList.Modem.1net4you.Dialup.Compression.AdressControl=False
DeviceList.Modem.1net4you.Dialup.Compression.BSD=False
DeviceList.Modem.1net4you.Dialup.Compression.CCP=False
DeviceList.Modem.1net4you.Dialup.Compression.ProtoField=False
DeviceList.Modem.1net4you.Dialup.Compression.VJID=False
DeviceList.Modem.1net4you.Dialup.Compression.VJTcpIp=False
DeviceList.Modem.1net4you.Dialup.DefRoute=True
DeviceList.Modem.1net4you.Dialup.DialMode=manual
DeviceList.Modem.1net4you.Dialup.Inherits=Modem0
DeviceList.Modem.1net4you.Dialup.HangupTimeout=600
DeviceList.Modem.1net4you.Dialup.Login=web
DeviceList.Modem.1net4you.Dialup.Password=web
DeviceList.Modem.1net4you.Dialup.Persist=False
DeviceList.Modem.1net4you.Dialup.PhoneNumber=019256252
DeviceList.Modem.1net4you.Dialup.ProviderName=1net4you
DeviceList.Modem.1net4you.Dialup.StupidMode=True
DeviceList.Modem.1net4you.IPv6Init=False
DeviceList.Modem.1net4you.OnBoot=False
DeviceList.Modem.1net4you.Type=Modem
DeviceList.TokenRing.tr0.AllowUser=False
DeviceList.TokenRing.tr0.AutoDNS=True
DeviceList.TokenRing.tr0.BootProto=dhcp
DeviceList.TokenRing.tr0.Device=tr0
DeviceList.TokenRing.tr0.DeviceId=tr0
DeviceList.TokenRing.tr0.IPv6Init=False
DeviceList.TokenRing.tr0.OnBoot=True
DeviceList.TokenRing.tr0.Type=TokenRing
DeviceList.Wireless.eth3.AllowUser=False
DeviceList.Wireless.eth3.AutoDNS=True
DeviceList.Wireless.eth3.BootProto=dhcp
DeviceList.Wireless.eth3.Device=eth3
DeviceList.Wireless.eth3.DeviceId=eth3
DeviceList.Wireless.eth3.IPv6Init=False
DeviceList.Wireless.eth3.OnBoot=False
DeviceList.Wireless.eth3.Type=Wireless
DeviceList.Wireless.eth3.Wireless.Channel=1
DeviceList.Wireless.eth3.Wireless.EssId=
DeviceList.Wireless.eth3.Wireless.Key=
DeviceList.Wireless.eth3.Wireless.Mode=Auto
DeviceList.Wireless.eth3.Wireless.Rate=auto
HardwareList.Ethernet.eth0.Card.ModuleName=3c501
HardwareList.Ethernet.eth0.Description=3c501
HardwareList.Ethernet.eth0.Name=eth0
HardwareList.Ethernet.eth0.Status=configured
HardwareList.Ethernet.eth0.Type=Ethernet
HardwareList.Ethernet.eth1.Card.ModuleName=3c501
HardwareList.Ethernet.eth1.Description=3c501
HardwareList.Ethernet.eth1.Name=eth1
HardwareList.Ethernet.eth1.Status=configured
HardwareList.Ethernet.eth1.Type=Ethernet
HardwareList.Ethernet.eth2.Card.ModuleName=3c501
HardwareList.Ethernet.eth2.Description=3c501
HardwareList.Ethernet.eth2.Name=eth2
HardwareList.Ethernet.eth2.Status=configured
HardwareList.Ethernet.eth2.Type=Ethernet
HardwareList.Ethernet.eth3.Card.ModuleName=3c501
HardwareList.Ethernet.eth3.Description=3c501
HardwareList.Ethernet.eth3.Name=eth3
HardwareList.Ethernet.eth3.Status=configured
HardwareList.Ethernet.eth3.Type=Ethernet
HardwareList.ISDN.ISDN Card 0.Card.ChannelProtocol=2
HardwareList.ISDN.ISDN Card 0.Card.DeviceId=
HardwareList.ISDN.ISDN Card 0.Card.DriverId=HiSax
HardwareList.ISDN.ISDN Card 0.Card.Firmware=
HardwareList.ISDN.ISDN Card 0.Card.IRQ=5
HardwareList.ISDN.ISDN Card 0.Card.IoPort1=
HardwareList.ISDN.ISDN Card 0.Card.IoPort2=
HardwareList.ISDN.ISDN Card 0.Card.IoPort=0x300
HardwareList.ISDN.ISDN Card 0.Card.Mem=
HardwareList.ISDN.ISDN Card 0.Card.ModuleName=hisax
HardwareList.ISDN.ISDN Card 0.Card.Type=30
HardwareList.ISDN.ISDN Card 0.Card.VendorId=
HardwareList.ISDN.ISDN Card 0.Description=ACER P10
HardwareList.ISDN.ISDN Card 0.Name=ISDN Card 0
HardwareList.ISDN.ISDN Card 0.Status=configured
HardwareList.ISDN.ISDN Card 0.Type=ISDN
HardwareList.Modem.Modem0.Description=Generic Modem
HardwareList.Modem.Modem0.Modem.BaudRate=115200
HardwareList.Modem.Modem0.Modem.DeviceName=/dev/modem
HardwareList.Modem.Modem0.Modem.DialCommand=ATDT
HardwareList.Modem.Modem0.Modem.FlowControl=CRTSCTS
HardwareList.Modem.Modem0.Modem.InitString=ATZ
HardwareList.Modem.Modem0.Modem.ModemVolume=0
HardwareList.Modem.Modem0.Name=Modem0
HardwareList.Modem.Modem0.Status=configured
HardwareList.Modem.Modem0.Type=Modem
HardwareList.TokenRing.tr0.Card.ModuleName=olympic
HardwareList.TokenRing.tr0.Description=olympic
HardwareList.TokenRing.tr0.Name=tr0
HardwareList.TokenRing.tr0.Status=configured
HardwareList.TokenRing.tr0.Type=TokenRing
ProfileList.default.Active=False
ProfileList.default.ActiveDevices.1=1net4you
ProfileList.default.ActiveDevices.2=1net4you0
ProfileList.default.ActiveDevices.3=eth0
ProfileList.default.ActiveDevices.4=eth3
ProfileList.default.ActiveDevices.5=tr0
ProfileList.default.DNS.Domainname=
ProfileList.default.DNS.Hostname=test
ProfileList.default.DNS.PrimaryDNS=1.1.1.1
ProfileList.default.DNS.SearchList.1=home
ProfileList.default.DNS.SecondaryDNS=2.2.2.2
ProfileList.default.DNS.TertiaryDNS=3.3.3.3
ProfileList.default.HostsList.1.AliasList.1=localhost
ProfileList.default.HostsList.1.Hostname=localhost.localdomain
ProfileList.default.HostsList.1.IP=127.0.0.1
ProfileList.default.HostsList.2.AliasList.1=localhost6
ProfileList.default.HostsList.2.Hostname=localhost6.localdomain6
ProfileList.default.HostsList.2.IP=::1
ProfileList.default.HostsList.3.AliasList.1=test1
ProfileList.default.HostsList.3.AliasList.2=test2
ProfileList.default.HostsList.3.Hostname=test
ProfileList.default.HostsList.3.IP=10.1.1.1
ProfileList.default.ProfileName=default
ProfileList.newprofile.Active=True
ProfileList.newprofile.ActiveDevices.1=1net4you
ProfileList.newprofile.ActiveDevices.2=1net4you0
ProfileList.newprofile.ActiveDevices.3=eth0
ProfileList.newprofile.ActiveDevices.4=eth3
ProfileList.newprofile.ActiveDevices.5=tr0
ProfileList.newprofile.DNS.Domainname=
ProfileList.newprofile.DNS.Hostname=test
ProfileList.newprofile.DNS.PrimaryDNS=1.1.1.1
ProfileList.newprofile.DNS.SearchList.1=home
ProfileList.newprofile.DNS.SecondaryDNS=2.2.2.2
ProfileList.newprofile.DNS.TertiaryDNS=3.3.3.3
ProfileList.newprofile.HostsList.1.AliasList.1=localhost
ProfileList.newprofile.HostsList.1.Hostname=localhost.localdomain
ProfileList.newprofile.HostsList.1.IP=127.0.0.1
ProfileList.newprofile.HostsList.2.AliasList.1=localhost6
ProfileList.newprofile.HostsList.2.Hostname=localhost6.localdomain6
ProfileList.newprofile.HostsList.2.IP=::1
ProfileList.newprofile.HostsList.3.AliasList.1=test1
ProfileList.newprofile.HostsList.3.AliasList.2=test2
ProfileList.newprofile.HostsList.3.Hostname=test
ProfileList.newprofile.HostsList.3.IP=10.1.1.1
ProfileList.newprofile.ProfileName=newprofile
"""
        self.redirectEnd()
        self.failUnless(expectConf(devstr, expect))

    def test03Profile(self):
        """Test profile removal"""
        self.redirectStd()
        from netconfpkg import NC_functions
        NC_functions.prepareRoot(CHROOT)
        devstr = self.getConf()

        from netconfpkg import  \
             NCDeviceList, NCProfileList, \
             NCHardwareList, NCIPsecList

        from netconfpkg.NC_functions import log
        profilelist = NCProfileList.getProfileList()
        NC_functions.setVerboseLevel(0)
        NC_functions.setDebugLevel(0)
        log.set_loglevel(NC_functions.getVerboseLevel())

        profilelist.remove(profilelist.getActiveProfile())
        profilelist.switchToProfile('default')
        profilelist.commit()
        self.save()
        NC_functions.setVerboseLevel(0)
        NC_functions.setDebugLevel(0)
        devstr = self.getConf()
        self.redirectEnd()
        expect = BASICSETUP
        self.failUnless(expectConf(expect, devstr))

    def save(self):
        from netconfpkg import NCProfileList
        profilelist = NCProfileList.getProfileList()
        profilelist.fixInterfaces()
        self.saveHardware()
        self.saveDevices()
        self.saveIPsecs()
        self.saveProfiles()

    def saveDevices(self):
        from netconfpkg import NCDeviceList
        devicelist = NCDeviceList.getDeviceList()
        devicelist.save()
        devicelist.setunmodified()

    def saveHardware(self):
        from netconfpkg import NCHardwareList
        hardwarelist = NCHardwareList.getHardwareList()
        hardwarelist.save()
        hardwarelist.setunmodified()

    def saveProfiles(self):
        from netconfpkg import NCProfileList
        profilelist = NCProfileList.getProfileList()
        profilelist.save()
        profilelist.setunmodified()

    def saveIPsecs(self):
        from netconfpkg import NCIPsecList
        ipseclist = NCIPsecList.getIPsecList()
        ipseclist.save()
        ipseclist.setunmodified()


# FIXME: check [165543] system-config-network-cmd - incorrect profile import - hosts file
# FIXME: check [165536] TB /usr/lib/python2.3/string.py:135:join:TypeError: sequence expected, NoneType found

def suite():
    suite = unittest.TestSuite()
    suite = unittest.makeSuite(TestRCN, 'test')
    return suite

if __name__ == "__main__":
    docoverage = False
    #docoverage = True
    if docoverage:
        import coverage
        coverage.erase()
        coverage.start()
    #import netconf_cmd
    #import netconfpkg
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
#            elif key.find("rhpl") != -1:
#                m.append(sys.modules[key])

        coverage.the_coverage.report(m, show_missing=0 )
        coverage.the_coverage.annotate(m, os.getcwd())
    #coverage.the_coverage.report(netconfpkg.NC_functions, show_missing=0 )
    #print sys.modules.keys()
    os.system("rm -fr %s" % CHROOT)

    sys.exit(not result.wasSuccessful())

__author__ = "Harald Hoyer <harald@redhat.com>"
