## Copyright (C) 2001-2007 Red Hat, Inc.

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

import dbus
from netconfpkg.NCHardware import HW_SYSTEM, Card
from netconfpkg.NC_functions import getDeviceType

HAL_DEVICE_IFACE = "org.freedesktop.Hal.Device"

class NCBackendHal:
    def __init__(self):
        self._dbusBus = dbus.SystemBus()
        self.halManagerObj = self._dbusBus.get_object("org.freedesktop.Hal",
                                         "/org/freedesktop/Hal/Manager")
        self.halManager = dbus.Interface(self.halManagerObj,
                                         "org.freedesktop.Hal.Manager")
        self.cards = []

    # ------------------------------------------------------------------------
    # Probe routines - HAL
    # ------------------------------------------------------------------------

    def getProperty(self, obj, prop):
        if not obj.PropertyExists(prop, dbus_interface=HAL_DEVICE_IFACE):
            return None
        return obj.GetProperty(prop, dbus_interface=HAL_DEVICE_IFACE)

    def getVendor(self, udi):
        parentUdi = udi
        while parentUdi and len(parentUdi):
            obj = self._dbusBus.get_object("org.freedesktop.Hal", parentUdi)

            vendor = self.getProperty(obj, "info.vendor")
            if vendor != None:
                return vendor, self.getProperty(obj, "info.product")

            new_parentUdi = self.getProperty(obj, "info.parent")
            if new_parentUdi == None:
                break
            parentUdi = new_parentUdi

    def getBus(self, udi):
        parentUdi = udi
        while parentUdi and len(parentUdi):
            obj = self._dbusBus.get_object("org.freedesktop.Hal", parentUdi)

            bus = self.getProperty(obj, "info.bus")
            if bus != None:
                return bus

            new_parentUdi = self.getProperty(obj, "info.parent")
            if new_parentUdi == None:
                break
            parentUdi = new_parentUdi

    def getDriver(self, udi):
        parentUdi = udi
        while parentUdi and len(parentUdi):
            obj = self._dbusBus.get_object("org.freedesktop.Hal", parentUdi)

            driver = self.getProperty(obj, "info.linux.driver")
            if driver != None:
                return driver

            new_parentUdi = self.getProperty(obj, "info.parent")
            if new_parentUdi == None:
                break
            parentUdi = new_parentUdi

    def getDevices(self, udi):
        obj = self._dbusBus.get_object("org.freedesktop.Hal", udi)
        category = self.getProperty(obj, "linux.subsystem")
        if category == "net" and self.getProperty(obj, "net.interface"):
            arp_proto_hw_id = self.getProperty(obj, "net.arp_proto_hw_id")
            if arp_proto_hw_id >= 256:
                return None

            from netconfpkg.NCHardwareFactory import getHardwareFactory
            hwf = getHardwareFactory()
            name = self.getProperty(obj, "net.interface")
            htype = getDeviceType(name)
            hwc = hwf.getHardwareClass(htype)
            if hwc:        
                hw = hwc()
                hw.Card = Card() 
                hw.Name = name
                hw.Type = htype
                hw.Description = ""
                try:
                    vendor = self.getVendor(udi)
                    if vendor:
                        hw.Description = "%s %s" % vendor
                except:
                    pass
 
                hw.Status = HW_SYSTEM

                index = self.getProperty(obj, "net.physical_device")
                if index != None:
                    
                    hw.Card.ModuleName = self.getDriver(index)

                return hw
        return None

    def probeCards(self):
        self.cards = []
        udiList = self.halManager.FindDeviceByCapability("net")
        for udi in udiList:
            ncard = self.getDevices(udi)
            if ncard:
                self.cards.append(ncard)
        return self.cards
