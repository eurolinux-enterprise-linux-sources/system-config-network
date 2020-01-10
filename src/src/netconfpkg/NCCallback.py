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
from netconfpkg.gdt import (Gdtstruct, gdtstruct_properties,
                            Gdtstr, Gdtbool, Gdtint)
from netconfpkg.NC_functions import log

class Callback_base(Gdtstruct):
    "Callback structure"
    gdtstruct_properties([
                          ('Delay', Gdtint, 'VALUE="3"'),
                          ('Hup', Gdtbool, "Test doc string"),
                          ('Compression', Gdtbool, "Test doc string"),
                          ('Type', Gdtstr, 'VALUE="on"'),
                          ('MSN', Gdtstr, "Test doc string"),
                          ])

    def __init__(self):
        super(Callback_base, self).__init__()
#        self.Delay = 3
        self.Delay = None
        self.Hup = None
        self.Compression = None
#        self.Type = "on"
        self.Type = None
        self.MSN = None

class Callback(Callback_base):
    boolkeydict = { 'Compression' : 'CBCP', 
                    'Hup' : 'CBHUP' }

    keydict = { 'Type' : 'CALLBACK', 
                'MSN' : 'CBCP_MSN', }

    intkeydict = { 'Delay' : 'CBDELAY' }

    def load(self, parentConf):
        conf = parentConf

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if conf.has_key(confkey):
                setattr(self, selfkey, conf[confkey])

        for selfkey in self.intkeydict.keys():
            confkey = self.intkeydict[selfkey]
            if conf.has_key(confkey) and len(conf[confkey]):
                setattr(self, selfkey, int(conf[confkey]))

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if conf.has_key(confkey):
                if conf[confkey] == 'on':
                    setattr(self, selfkey, True)
                else:
                    setattr(self, selfkey, False)
            else:
                setattr(self, selfkey, False)

    def save(self, parentConf):
        log.log(6, "in Callback.save")
        conf = parentConf

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if hasattr(self, selfkey):
                conf[confkey] = getattr(self, selfkey)
            else: conf[confkey] = ""

        for selfkey in self.intkeydict.keys():
            confkey = self.intkeydict[selfkey]
            if hasattr(self, selfkey):
                conf[confkey] = getattr(self, selfkey)
            else: conf[confkey] = ""

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if hasattr(self, selfkey) and getattr(self, selfkey):
                conf[confkey] = 'on'
            else:
                conf[confkey] = 'off'
        log.log(6, "in Callback.save end")



__author__ = "Harald Hoyer <harald@redhat.com>"
