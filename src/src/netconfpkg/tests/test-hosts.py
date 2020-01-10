#!/usr/bin/python
# -*- coding: utf-8 -*-

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

def expectConf(**kwargs):
    if kwargs.has_key("expectstr"):
        exlines = kwargs.get("expectstr")
        exlines = string.split(exlines, '\n')
        if kwargs.get("sort"):
            exlines.sort()
        if exlines[0] == "":
            exlines = exlines[1:]
    elif kwargs.has_key("expectfile"):
        filename = kwargs.get("expectfile")
        if not os.path.isfile(filename):
            raise IOError
        file = open(filename, 'r', -1)
        exlines = file.readlines()
        if kwargs.get("sort"):
            exlines.sort()
        for i in xrange(len(exlines)):
            exlines[i]=exlines[i].strip()
    else:
        raise ValueError


    if kwargs.has_key("filename"):
        filename = kwargs.get("filename")
        if not os.path.isfile(filename):
            raise IOError

        file = open(filename, 'r', -1)
        lines = file.readlines()
        if kwargs.get("sort"):
            lines.sort()
        for i in xrange(len(lines)):
            lines[i]=lines[i].strip()

    elif kwargs.has_key("lines"):
        lines = string.split(kwargs.get("lines"), '\n')
        if kwargs.get("sort"):
            lines.sort()
        for i in xrange(len(lines)):
            lines[i]=lines[i].strip()
        while "" in lines:
            lines.remove("")
    else:
        raise ValueError

    l = max(len(lines), len(exlines))

    equal = True

    for i in xrange(l):
        oline = ""
        exline= ""
        if i < len(lines):
            oline = lines[i]
        if i < len(exlines):
            exline = exlines[i]
        if (oline != exline):
            print "\n- %s\n+ %s\n" % (exline, oline)
            equal = False
            break

    if equal:
        return True

    print "Output (%d lines):" % len(lines)
    print "---------------------"
    sys.stdout.write(string.join(lines, "\n"))
    print "---------------------"
    return False



class TestHosts(unittest.TestCase):
    def test00Basic(self):
        """Testing basic reading from a /etc/hosts file"""
        from netconfpkg import NC_functions
        from netconfpkg.NCHostsList import HostsList

        hl = HostsList()
        hl.load(filename=srcdir+"/hosts")

        expect = """HostsList.1.AliasList.1=localhost
HostsList.1.Hostname=localhost.localdomain
HostsList.1.IP=127.0.0.1
HostsList.2.AliasList.1=localhost6
HostsList.2.Hostname=localhost6.localdomain6
HostsList.2.IP=::1
HostsList.3.AliasList.1=test3
HostsList.3.Hostname=test2
HostsList.3.IP=10.1.1.2
"""
        self.failUnless(expectConf(sort=True, 
                                   expectstr=expect, 
                                   lines=str(hl)))


    def test01Add(self):
        """Test of adding a host entry"""
        from netconfpkg import NC_functions
        from netconfpkg.NCHostsList import HostsList
        from netconfpkg.NCHost import Host

        hl = HostsList()
        hl.load(filename=srcdir+"/hosts")
        h = Host()
        h.Hostname = "test4"
        h.IP = "10.1.1.1"
        hl.append(h)
        h.commit()
        hl.commit()

        expect = """HostsList.1.AliasList.1=localhost
HostsList.1.Hostname=localhost.localdomain
HostsList.1.IP=127.0.0.1
HostsList.2.AliasList.1=localhost6
HostsList.2.Hostname=localhost6.localdomain6
HostsList.2.IP=::1
HostsList.3.AliasList.1=test3
HostsList.3.Hostname=test2
HostsList.3.IP=10.1.1.2
HostsList.4.Hostname=test4
HostsList.4.IP=10.1.1.1
"""
        self.failUnless(expectConf(sort=True, 
                                   expectstr=expect, 
                                   lines=str(hl)))


    def test02Modify(self):
        """Test of modifying a host entry"""
        from netconfpkg import NC_functions
        from netconfpkg.NCHostsList import HostsList
        from netconfpkg.NCHost import Host

        hl = HostsList()
        hl.load(filename=srcdir+"/hosts")
        for host in hl:
            if host.Hostname == "test2":
                host.IP = "10.1.1.3"
                host.commit()
        hl.commit()
        hl.save(filename="hosts2.new")

        self.failUnless(expectConf(expectfile = srcdir+"/hosts2", filename="hosts2.new"))

        os.unlink("hosts2.new")
        
    def test03WrongEntry(self):
        """ Test parsing hosts file with containing wrong entries """
        from netconfpkg import NC_functions
        from netconfpkg.NCHostsList import HostsList
        from netconfpkg.NCHost import Host
        # expected errors in config file
        badlines = [(7, 'IP'), (8, 'Hostname'), (9, 'Alias'), (10, 'Hostname')]
        hl = HostsList()
        try:
            hl.load(srcdir+"/hosts_bad")
        except Exception, e:
            self.failUnless(e.badlines == badlines)
                

def suite():
    suite = unittest.TestSuite()
    suite = unittest.makeSuite(TestHosts, 'test')
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

        coverage.the_coverage.report(m, show_missing=0 )
        coverage.the_coverage.annotate(m, os.getcwd())

    sys.exit(not result.wasSuccessful())

__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/03/14 13:39:43 $"
__version__ = "$Revision: 1.10 $"
