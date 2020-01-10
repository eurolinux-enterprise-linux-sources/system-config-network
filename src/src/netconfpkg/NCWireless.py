## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001, 2002 Than Ngo <than@redhat.com>
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>
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
import re
from netconfpkg import NC_functions
from netconfpkg.gdt import (Gdtstruct, gdtstruct_properties, 
                            Gdtstr)


class Wireless_base(Gdtstruct):
    gdtstruct_properties([
                          ('Mode', Gdtstr, "Test doc string"),
                          ('EssId', Gdtstr, "Test doc string"),
                          ('Channel', Gdtstr, "Test doc string"),
                          ('Rate', Gdtstr, "Test doc string"),
                          ('Key', Gdtstr, "Test doc string"),
                          ])

class Wireless(Wireless_base):
    keydict = { 'Mode' : 'MODE', 
                'EssId' : 'ESSID', 
                'Channel' : 'CHANNEL', 
                'Rate' : 'RATE', 
                'Key' : 'KEY', 
                }

    def __init__(self):
        super(Wireless, self).__init__()
        self.Key = ''

    def load(self, parentConf, deviceid):
        
        conf = parentConf

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if conf.has_key(confkey):
                setattr(self, selfkey, conf[confkey])

        conf = NC_functions.ConfKeys(deviceid)
        if conf.has_key("KEY"):
            self.Key = conf["KEY"]
        del conf


        if re.search("^s:", self.Key):
            self.Key = self.Key[2:]
        elif re.search("^[0-9a-fA-F]+$", self.Key):
            self.Key = "0x" + self.Key


    def save(self, parentConf, deviceid):
        
        conf = parentConf

        keyconf = NC_functions.ConfKeys(deviceid)
        keyconf.fsf()
        if re.search("^\s*0x[0-9a-fA-F]+\s*$", self.Key):
            keyconf["KEY"] = self.Key[2:]
        elif re.search("^\s*[^\s]+\s*$", self.Key):
            keyconf["KEY"] = "s:" + self.Key
        else:
            keyconf["KEY"] = self.Key
        keyconf.write()
        # FIXME: [167995] Wireless card mode cannot be set to Auto
        # FIXME: [162830] activate notifier box does not presist long 
        # enough to read it
        # check, if the interface support RATE, FREQ, etc.
        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if hasattr(self, selfkey) and getattr(self, selfkey) != None:
                conf[confkey] = getattr(self, selfkey)
            else: del conf[confkey]
            #conf[confkey] = ""

        if conf.has_key("KEY"):
            del conf["KEY"]

        # Do not clear the non-filled in values
        # Bugzilla #52252
        # for i in conf.keys():
        #    if not conf[i] or conf[i] == "": del conf[i]

        # the key is now stored in a seperate file
        # conf.oldmode = 0600
        # conf.chmod(0600)
__author__ = "Harald Hoyer <harald@redhat.com>"
__date__ = "$Date: 2007/07/13 12:49:00 $"
__version__ = "$Revision: 1.23 $"
