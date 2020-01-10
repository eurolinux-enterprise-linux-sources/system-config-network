## Copyright (C) 2001-2005 Red Hat, Inc.
## Copyright (C) 2001-2005 Harald Hoyer <harald@redhat.com>

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
from netconfpkg.NCHardware import Hardware
from netconfpkg.NC_functions import log

_hwFac = None

def getHardwareFactory():
    global _hwFac  # pylint: disable-msg=W0603

    if _hwFac == None:
        _hwFac = HardwareFactory()

    return _hwFac


class HardwareFactory(dict):
    def register(self, theclass, hwtype = None, subtype = None):
        if not issubclass(theclass, Hardware):
            raise ValueError, "First argument has to be a subclass of Hardware!"

        if not hwtype:
            if hasattr(theclass, "Type"):
                hwtype = theclass.Type
            else:
                return

        if not subtype and hasattr(theclass, "SubType"):
            subtype = theclass.SubType

        if not subtype:
            if self.has_key(hwtype):
            #raise KeyError, "%s is already registered" % hwtype
                log.log(1, "KeyError, %s is already registered" % hwtype)
                return
            else:
                self[hwtype] = { 0 : theclass }
        else:
            if self.has_key(hwtype) and self[hwtype].has_key(subtype):
                #raise KeyError, "%s.%s is already registered" 
                #                % (hwtype, subtype)
                log.log(1, "KeyError %s.%s is already registered" 
                        % (hwtype, subtype))
                return
            else:
                if not self.has_key(hwtype):
                    self[hwtype] = {}
                self[hwtype][subtype] = theclass

    def getHardwareClass(self, hwtype, subtype = None):
        if not self.has_key(hwtype):
            log.log(1, "Error: %s not in HardwareFactory!" % hwtype)
            return Hardware
        if subtype and self[type].has_key(subtype):
            return self[hwtype][subtype]
        else:
            return self[hwtype][0]

# pylint: disable-msg=W0401, W0614
from netconfpkg.plugins import * # DO NOT MOVE FROM BOTTOM!!

__author__ = "Harald Hoyer <harald@redhat.com>"
