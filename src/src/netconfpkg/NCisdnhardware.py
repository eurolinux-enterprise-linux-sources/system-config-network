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
import commands
import os
from netconfpkg.NC_functions import getRoot, ISDNCARDCONF, log
from netconfpkg.conf import ConfShellVar


TYPE = 0
IRQ = 1
IO = 2
IO1 = 3
IO2 = 4
MEM = 5
VENDOR_ID = 6
DEVICE_ID = 7
DRIVER_ID = 8
FIRMWARE = 9
MODUL = 10

_card = {
    # "ISDN Adapter" : [ type, irq, io, io1, io2, mem, vendor_id,
    #                    device_id, driver_id, firmware, module ]
    "ACER P10" : [ "30", "5", "0x300", "", "", "", "", "", "HiSax", "",
                   "hisax" ],
    "ASUS COM ISDNLink ISA PnP" : [ "12", "", "", "", "", "", "ASU1690",
                                    "ASU1690", "HiSax", "", "hisax" ],
    "ASUS COM ISDNLink PCI" : [ "35", "", "", "", "", "", "", "", "HiSax",
                                "", "hisax" ],
    "AVM A1 (Fritz)" : [ "5", "10", "0x300", "", "", "", "", "", "HiSax",
                         "",  "hisax" ],
    "AVM Fritz Card PCMCIA" : [ "", "", "", "", "", "", "", "", "", "",
                                "avma1_cs" ],
    "AVM PCI (Fritz!PCI)" : [ "27", "", "", "", "", "", "1244", "0a00",
                              "HiSax", "", "hisax" ],
    "AVM PCI (Fritz!PCI v2)" : [ "0", "", "", "", "", "", "1244", "0e00",
                                 "", "", "hisax_fcpcipnp" ],
    "AVM PnP" : [ "27", "", "", "", "", "", "AVM0900", "AVM0900", "HiSax",
                  "", "hisax" ],
    "Billion ISDN P&P PCI 128k Cologne SE" : [ "35", "", "", "", "", "",
                                               "1397", "2bd0", "HiSax", "",
                                               "hisax" ],
    "Compaq ISDN S0 ISA" : [ "19", "5", "0x0000", "0x0000", "0x0000", "", "",
                             "", "HiSax", "", "hisax" ],
    "Creatix Teles PnP" : [ "4", "", "", "", "", "", "", "", "HiSax", "",
                            "hisax" ],
    "Dr. Neuhaus Niccy PnP" : [ "24", "", "", "", "", "", "", "", "HiSax",
                                "", "hisax" ],
    "Dr. Neuhaus Niccy PCI" : [ "24", "", "", "", "", "", "1267", "1016",
                                "HiSax", "", "hisax" ],
    "Dynalink 128PH PCI" : [ "36", "", "", "", "", "", "", "", "HiSax", "",
                             "hisax" ],
    "Eicon.Diehl Diva ISA PnP" : [ "11", "", "", "", "", "", "", "", "HiSax",
                                   "", "hisax" ],
    "Eicon.Diehl Diva 20PRO PCI" : [ "11", "", "", "", "", "", "1133", "e001",
                                     "HiSax", "", "hisax" ],
    "Eicon.Diehl Diva 20 PCI" : [ "11", "", "", "", "", "", "1133", "e002",
                                  "HiSax", "", "hisax" ],
    "Eicon.Diehl Diva 20PRO_U PCI" : [ "11", "", "", "", "", "", "1133",
                                       "e003", "HiSax", "", "hisax" ],
    "Eicon.Diehl Diva 20_U PCI" : [ "11", "", "", "", "", "", "1133", "e004",
                                    "HiSax", "", "hisax" ],
    "ELSA PCC/PCF" : [ "6", "", "", "", "", "", "", "", "HiSax", "", "hisax" ],
    "ELSA Quickstep 1000" : [ "7", "5", "0x300", "", "", "", "ELS0133",
                              "ELS0133", "HiSax", "", "hisax" ],
    "ELSA Quickstep 1000 PCI" : [ "18", "", "", "", "", "", "1048", "1000",
                                  "HiSax", "", "hisax" ],
    "ELSA Quickstep 3000 PCI" : [ "18", "", "", "", "", "", "1048", "3000",
                                  "HiSax", "", "hisax" ],
    "ELSA PCMCIA MicroLink cards" : [ "", "", "", "", "", "", "", "", "", "",
                                      "elsa_cs" ],
    "Gazel cards ISA" : [ "34", "5", "0x300", "", "", "", "", "", "HiSax", "",
                          "hisax" ],
    "Gazel cards PCI" : [ "34", "", "", "", "", "", "10b5", "1030", "HiSax",
                          "", "hisax" ],
    "HFC-2BS0 based cards ISA" : [ "13", "9", "0xd80", "", "", "", "", "",
                                   "HiSax", "", "hisax" ],
    "HFC-2BS0 based cards PCI" : [ "35", "", "", "", "", "", "1397", "2bd0",
                                  
                                   "HiSax", "", "hisax" ],
    "HST Saphir" : [ "31", "5", "0x300", "", "", "", "", "", "HiSax", "",
                     "hisax" ],
    "ITK ix1-micro Rev.2" : [ "9", "9", "0xd80", "", "", "", "", "", "HiSax",
                              "", "hisax" ],
    "MIC card" : [ "17", "9", "0xd80", "", "", "", "", "", "HiSax", "",
                   "hisax" ],
    "NETjet PCI" : [ "20", "", "", "", "", "", "e159", "0001", "HiSax", "",
                     "hisax" ],
    "Sedlbauer PC 104" : [ "15", "9", "0xd80", "", "", "", "", "", "HiSax",
                           "", "hisax" ],
    "Sedlbauer Speed PCI" : [ "15", "", "", "", "", "", "", "", "HiSax", "",
                              "hisax" ],
    "Sedlbauer Speed Card" : [ "15", "9", "0xd80", "", "", "", "", "",
                               "HiSax", "", "hisax" ],
    "Sedlbauer Speed Fax+" : [ "28", "3", "0x200", "", "", "", "SAG0002",
                               "SAG0002", "HiSax",
                               "hisaxctrl HiSax 9 /usr/lib/isdn/ISAR.BIN",
                               "hisax" ],
    "Sedlbauer Speed fax+ PCI" : [ "28", "", "", "", "", "", "e159", "0002",
                                   "HiSax",
                                   "hisaxctrl HiSax 9 /usr/lib/isdn/ISAR.BIN",
                                   "hisax" ],
    "Sedlbauer Speed Star PCMCIA Card" : [ "", "", "", "", "", "", "", "", "",
                                           "", "sedlbauer_cs" ],
    "Siemens I-Surf 1.0" : [ "29", "9", "0xd80", "", "", "0xd000", "", "",
                             "HiSax", "", "hisax" ],
    "Telekom A4T" : [ "32", "", "", "", "", "", "", "", "HiSax", "", "hisax" ],
    "Teles 8.0" : [ "2", "9", "", "", "", "0xd800", "", "", "HiSax", "",
                    "hisax" ],
    "Teles 16.0" : [ "1", "5", "0xd80", "", "", "0xd000", "", "", "HiSax",
                     "", "hisax" ],
    "Teles 16.3" : [ "3", "9", "0xd80", "", "", "", "", "", "HiSax", "",
                     "hisax" ],
    "Teles 16.3c PnP" : [ "14", "", "", "", "", "", "TAG2610", "TAG2610",
                          "HiSax", "", "hisax" ],
    "Teles PCI" : [ "21", "", "", "", "", "", "", "", "HiSax", "", "hisax" ],
    "Teles PnP" : [ "4", "", "", "", "", "", "", "", "HiSax", "", "hisax" ],
    "Teles S0Box" : [ "25", "7", "0x378", "", "", "", "", "", "HiSax", "",
                      "hisax" ],
    "USR Sportster intern" : [ "16", "9", "0xd80", "", "", "", "", "",
                               "HiSax", "", "hisax" ],
    "W6692 based PCI cards" : [ "36", "", "", "", "", "", "1050", "6692",
                                "HiSax", "", "hisax" ]
    }


def getCards():
    return _card

class ConfISDN:
    keydict = { 'Description' : 'NAME',
                'ModuleName' : 'MODULE',
                'VendorId' : 'VENDOR_ID',
                'Firmware' : 'FIRMWARE',
                'Resources' : 'RESOURCES'
                }
    def __init__(self):
        self.Description = ""
        self.ChannelProtocol = "2"
        self.Type = ""
        self.IRQ = ""
        self.IoPort = ""
        self.IoPort1 = ""
        self.IoPort2 = ""
        self.Mem = ""
        self.VendorId = ""
        self.DeviceId = ""
        self.DriverId = ""
        self.Firmware = ""
        self.ModuleName = ""
        self.Resources = ""

    def get_value(self, s):
        if s.find("=") < 0:
            return ""
        s = s.split("=", 1)[1]
        s = s.replace("\"", "")

        return s.strip()

    def load(self, f = None):

        if not f:
            f = getRoot() + ISDNCARDCONF
        if not os.path.exists(f):
            return -1

        mconf = ConfShellVar.ConfShellVar(filename = f)
        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if mconf.has_key(confkey):
                setattr(self, selfkey, mconf[confkey])

        log.log(5, "RESOURCES=%s" % self.Resources)

        rlist = self.Resources.split(" ")
        for i in rlist:
            log.log(5, "%s" % i)
            if i.find("type=") == 0:
                self.Type = self.get_value(i)
            elif i.find("protocol=") == 0:
                self.ChannelProtocol = self.get_value(i)
            elif i.find("irq=") == 0:
                self.IRQ = self.get_value(i)
            elif i.find("id=") == 0:
                self.DriverId = self.get_value(i)
            elif i.find("io=") == 0 or i.find("io0=") == 0:
                self.IoPort = self.get_value(i)
            elif i.find("io1=") == 0:
                self.IoPort1 = self.get_value(i)
            elif i.find("io2=") == 0:
                self.IoPort2 = self.get_value(i)
            elif i.find("mem=") == 0:
                self.Mem = self.get_value(i)

        if len(rlist) and not self.Type:
            self.Type = '0'

        return 1

    def save(self, f = None):
        if f == None:
            f = getRoot() + ISDNCARDCONF
        # we only support 1 ISDN card in this version
        if not self.Description:
            if os.path.exists(f):
                os.unlink(f)
            return

        conf = ConfShellVar.ConfShellVar(filename = f)

        rs = ""
        if self.Type:
            rs = rs + "protocol=" + str(self.ChannelProtocol)
            if self.Type == '0':
                pass
            else:
                rs = rs + " type=" + str(self.Type)
                if self.IRQ:
                    rs = rs + " irq=" + str(self.IRQ)
                if self.DriverId:
                    rs = rs + " id=" + str(self.DriverId)
                if self.IoPort:
                    if (self.Type == "4" 
                        or self.Type == "19" 
                        or self.Type == "24"):
                        rs = rs + " io0=" + str(self.IoPort)
                    else:
                        rs = rs + " io=" + str(self.IoPort)
                if self.IoPort1:
                    rs = rs + " io1=" + str(self.IoPort1)
                if self.IoPort2:
                    rs = rs + " io2=" + str(self.IoPort2)
                if self.Mem:
                    rs = rs + " mem=" + str(self.Mem)
        else:
            rs = rs + "NONE"

        self.Resources = rs

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if hasattr(self, selfkey):
                conf[confkey] = getattr(self, selfkey)
            else: conf[confkey] = ""


        conf.write()


    def cleanup(self, f = None):
        if f == None:
            f = getRoot() + ISDNCARDCONF
        # we only support 1 ISDN card in this version
        if not self.Description:
            if os.path.exists(f):
                os.unlink(f)
            return


    def detect(self):
        fpci = '/sbin/lspci'
        fpnp = '/proc/bus/isapnp/devices'
        found = 0
        idl = []
        if os.path.exists(fpci):
            pci_infos = commands.getoutput(fpci + ' -n 2>/dev/null')
            found = 1
        if os.path.exists(fpnp):
            f = open(fpnp, 'r')
            line = f.readline()
            while line:
                idl.append(line.split()[1])
                line = f.readline()
            f.close()
            found = 1

        if found == 0: 
            return

        for i in _card.keys():
            if _card[i][VENDOR_ID] and _card[i][DEVICE_ID]:
                if pci_infos.find(_card[i][VENDOR_ID] 
                                  + ':' + _card[i][DEVICE_ID]) >0:
                    return {i : _card[i]}
                elif idl and idl.count(_card[i][VENDOR_ID] 
                                       + _card[i][DEVICE_ID]) >0:
                    return {i : _card[i]}

    def get_resource(self, name):
        if _card.has_key(name):
            # FIXME: remove Cardinfo
            self.Description = name
            self.Type = _card[name][TYPE]
            self.IRQ = _card[name][IRQ]
            self.IoPort = _card[name][IO]
            self.IoPort1 = _card[name][IO1]
            self.IoPort2 = _card[name][IO2]
            self.Mem = _card[name][MEM]
            self.VendorId = _card[name][VENDOR_ID]
            self.DeviceId = _card[name][DEVICE_ID]
            self.DriverId = _card[name][DRIVER_ID]
            self.Firmware = _card[name][FIRMWARE]
            self.ModuleName = _card[name][MODUL]

__author__ = "Than Ngo <than@redhat.com>"

