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
from netconfpkg.NCDevice import Device
from netconfpkg.NC_functions import log

_devFac = None


class DeviceFactory(dict):
    def register(self, theclass, devtype = None, subtype = None):

        if devtype == None and hasattr(theclass, "Type"):
            devtype = theclass.Type
        if subtype == None and hasattr(theclass, "SubType"):
            subtype = theclass.SubType

        log.log(5, "Register %s %s" % (str(theclass), str(devtype)))

        if not issubclass(theclass, Device):
            raise ValueError, "first argument has to be a subclass of Device"

        if not subtype:
            if self.has_key(devtype):
                #raise KeyError, "%s is already registered" % devtype
                log.log(1, "KeyError, %s is already registered" % devtype)
                return
            else:
                self[devtype] = { 0 : theclass }
        else:
            if self.has_key(devtype) and self[devtype].has_key(subtype):
                log.log(1, "KeyError, %s.%s is already registered" 
                        % (devtype, subtype))
                return
            else:
                if not self.has_key(devtype):
                    self[devtype] = {}
                self[devtype][subtype] = theclass

    def getDeviceClass(self, devtype, subtype = None):
        if not self.has_key(devtype):
            log.log(1, "Error: %s not in DeviceFactory!" % devtype)
            return Device

        if subtype and self[devtype].has_key(subtype):
            return self[devtype][subtype]
        else:
            return self[devtype][0]

def getDeviceFactory():
    global _devFac # pylint: disable-msg=W0603

    if _devFac == None:
        _devFac = DeviceFactory()

    return _devFac

# pylint: disable-msg=W0401, W0614
from netconfpkg.plugins import * # DO NOT MOVE FROM BOTTOM!!

__author__ = "Harald Hoyer <harald@redhat.com>"
