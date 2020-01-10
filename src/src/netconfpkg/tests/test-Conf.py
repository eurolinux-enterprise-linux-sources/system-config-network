#!/usr/bin/python

import unittest
import sys
import string
import os

sys.path.append(os.getcwd() + "/../../")

if os.environ.has_key("srcdir"):
    srcdir = os.environ["srcdir"]
    sys.path.append(srcdir + "/../../")
else:
    srcdir = os.getcwd()


def writeConf(filename, str):
    try: os.unlink(filename)
    except OSError: pass
    file = open(filename, 'w', -1)
    file.write(str)
    file.close()

def expectConf(filename, str):
    if not os.path.isfile(filename):
        return 1

    file = open(filename, 'r', -1)
    lines = file.readlines()
    lines = string.join(lines, '')

    return (lines == str)

class TestConf(unittest.TestCase):
    filename = "test.out"
    def tearDown(self):
        try:
            os.unlink(self.filename)
        except: pass

    def test01ReadWrite(self):
        """Conf class: basic reading and writing"""
        str = """
# testConfig file
a\tb
# comment
c\td
# comment2
"""
        # read
        writeConf(self.filename, str)
        from netconfpkg.conf import Conf
        conf = Conf.Conf(self.filename)
        os.unlink(self.filename)
        # write
        conf.write()
        del conf
        # check
        if not expectConf(self.filename, str):
            writeConf(self.filename + '.orig', str)
            os.system("(echo;diff -u  %s %s) >&2" % (self.filename + ".orig", self.filename))
            os.unlink(self.filename + '.orig')
            self.fail("Test1 failed!!!!")


    def test02Modify(self):
        """Conf class: reading, modify and writing"""
        str = """
# testConfig file
a=b
# comment
c=d 
# comment2
"""
        # read
        writeConf(self.filename, str)
        from netconfpkg.conf import ConfShellVar
        conf = ConfShellVar.ConfShellVar(self.filename)
        os.unlink(self.filename)
        # modify
        conf["a"] = "e"
        conf["c"] = "f"
        conf["g"] = "h"
        # write
        conf.write()
        del conf
        # check
        str = """
# testConfig file
a=e
# comment
c=f
# comment2
g=h
"""
        if not expectConf(self.filename, str):
            writeConf(self.filename + '.orig', str)
            os.system("(echo;diff -u  %s %s) >&2" % (self.filename + ".orig", self.filename))
            os.unlink(self.filename + '.orig')
            self.fail("Test2 failed!!!!")


    def test03ConfModules(self):
        """ConfModules class: basic reading and writing"""
        #
        # test3
        #
        str = """# Modules test file
alias parport_lowlevel parport_pc
#alias eth0 3c59x
alias eth3 3c59x # test test
alias eth3 3c59x # test test2
#alias eth0 3c59x
#alias sound-slot-1 emu10k1
alias sound-slot-0 emu10k1
#alias sound-slot-1 emu10k1
# comment comment
post-install sound-slot-0 /bin/aumix-minimal -f /etc/.aumixrc -L >/dev/null 2>&1 || :
pre-remove sound-slot-0 /bin/aumix-minimal -f /etc/.aumixrc -S >/dev/null 2>&1 || :alias usb-controller usb-uhci
post-install sound-slot-1 /bin/aumix-minimal -f /etc/.aumixrc -L >/dev/null 2>&1 || :
install snd-via82xx-modem /bin/true # temporarily disabled by hsf - conflicts with hsfmc97via
options snd-intel8x0 index=0 id="ICH"
options snd cards_limit=2
alias char-major-195* nvidia
alias eth4 3c501
alias foo* bar
# LAST LINE
"""
        # read
        writeConf(self.filename, str)
        from netconfpkg.conf.ConfModules import ConfModules
        conf = ConfModules(self.filename)
        os.unlink(self.filename)
        # write
        conf.write()
        del conf
        # check
        if not expectConf(self.filename, str):
            writeConf(self.filename + '.orig', str)
            os.system("(echo;diff -u  %s %s) >&2" % (self.filename + ".orig", self.filename))
            os.unlink(self.filename + '.orig')
            self.fail("Test3 failed!!!!")

    def test04ConfModulesModify(self):
        """ConfModules class: reading, modify and writing"""
        #
        # test4
        #
        str = """# Modules test file
alias parport_lowlevel parport_pc
#alias eth0 3c59x
alias eth3 3c59x
#alias eth0 3c59x
#alias sound-slot-1 emu10k1
alias sound-slot-0 emu10k1
#alias sound-slot-1 emu10k1
# comment comment
post-install sound-slot-0 /bin/aumix-minimal -f /etc/.aumixrc -L >/dev/null 2>&1 || :
pre-remove sound-slot-0 /bin/aumix-minimal -f /etc/.aumixrc -S >/dev/null 2>&1 || :alias usb-controller usb-uhci
post-install sound-slot-1 /bin/aumix-minimal -f /etc/.aumixrc -L >/dev/null 2>&1 || :
install snd-via82xx-modem /bin/true # temporarily disabled by hsf - conflicts with hsfmc97via
#options ipw2100 ifname=eth1
options i8k force=1
options snd-intel8x0 index=0 id="ICH"
options snd cards_limit=2
options parport_pc io=0x378 irq=7
options nsc-ircc io=0x02f8 dongle_id=0x09 irq=3 dma=0
options 3c59x debug=2
alias char-major-195* nvidia
alias eth0 3c59xsss
alias foo* bar
# LAST LINE
"""
        # read
        writeConf(self.filename, str)
        from netconfpkg.conf.ConfModules import ConfModules
        conf = ConfModules(self.filename)
        os.unlink(self.filename)
        # modify
        conf["eth3"]["alias"] = "3c59xaaa"
        conf["eth0"] = { "alias" : "3c59x" }
        conf["foo*"] = { "alias" : "baz" }
        # write
        conf.write()
        del conf
        # check
        str = """# Modules test file
alias parport_lowlevel parport_pc
#alias eth0 3c59x
alias eth3 3c59xaaa
#alias eth0 3c59x
#alias sound-slot-1 emu10k1
alias sound-slot-0 emu10k1
#alias sound-slot-1 emu10k1
# comment comment
post-install sound-slot-0 /bin/aumix-minimal -f /etc/.aumixrc -L >/dev/null 2>&1 || :
pre-remove sound-slot-0 /bin/aumix-minimal -f /etc/.aumixrc -S >/dev/null 2>&1 || :alias usb-controller usb-uhci
post-install sound-slot-1 /bin/aumix-minimal -f /etc/.aumixrc -L >/dev/null 2>&1 || :
install snd-via82xx-modem /bin/true # temporarily disabled by hsf - conflicts with hsfmc97via
#options ipw2100 ifname=eth1
options i8k force=1
options snd-intel8x0 index=0 id="ICH"
options snd cards_limit=2
options parport_pc io=0x378 irq=7
options nsc-ircc io=0x02f8 dongle_id=0x09 irq=3 dma=0
options 3c59x debug=2
alias char-major-195* nvidia
alias eth0 3c59x
alias foo* baz
# LAST LINE
"""
        if not expectConf(self.filename, str):
            writeConf(self.filename + '.orig', str)
            os.system("(echo;diff -u  %s %s) >&2" % (self.filename + ".orig", self.filename))
            os.unlink(self.filename + '.orig')
            self.fail("Test4 failed!!!!")

def suite():
    suite = unittest.TestSuite()
    suite = unittest.makeSuite(TestConf, 'test')
    return suite

if __name__ == "__main__":
    do_coverage = False
    #do_coverage = True
    if do_coverage:
        import coverage
        coverage.erase()
        coverage.start()

    from netconfpkg.conf import *
    testRunner = unittest.TextTestRunner(verbosity=2)
    result = testRunner.run(suite())

    if do_coverage:
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
            if key.find("netconfpkg.conf") != -1:
                m.append(sys.modules[key])
        
        coverage.the_coverage.report(m, show_missing=0 )

    sys.exit(not result.wasSuccessful())

__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/07/13 13:03:49 $"
__version__ = "$Revision: 1.15 $"
