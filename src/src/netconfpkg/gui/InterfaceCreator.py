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
from netconfpkg.NCDeviceList import getDeviceList
from netconfpkg.NCHardwareList import getHardwareList
from netconfpkg.NCProfileList import getProfileList


class InterfaceCreator:
    def __init__(self, do_save = 1):
        self.do_save = do_save

    def get_project_name(self):
        raise NotImplementedError

    def get_project_description(self):
        raise NotImplementedError

    def get_druids(self):
        raise NotImplementedError

    def save(self):
        self.saveDevices()
        self.saveHardware()
        self.saveProfiles()

    def getNextAlias(self, device):
        devicelist = getDeviceList()
        alias = None
        for dev in devicelist:
            if not dev.Device == device.Device:
                continue
            if dev.Alias:
                if alias == None:
                    alias = dev.Alias + 1
                elif alias <= dev.Alias:
                    alias = dev.Alias + 1
            elif alias == None:
                alias = 1
        return alias

    def saveDevices(self):
        if not self.do_save:
            return
        devicelist = getDeviceList()
        devicelist.save()

    def saveHardware(self):
        if not self.do_save:
            return
        hardwarelist = getHardwareList()
        hardwarelist.save()

    def saveProfiles(self):
        if not self.do_save:
            return
        profilelist = getProfileList()
        profilelist.save()
        
__author__ = "Harald Hoyer <harald@redhat.com>"
