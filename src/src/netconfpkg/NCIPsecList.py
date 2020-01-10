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

#from netconfpkg import IPsecList_base # pylint: disable-msg=E0611
import os
from netconfpkg.NCDeviceList import ConfDevices
from netconfpkg.NCIPsec import IPsec
from netconfpkg.NC_functions import (log, SYSCONFDEVICEDIR, getRoot,
                                     testFilename, IPSEC, unlink, 
                                     OLDSYSCONFDEVICEDIR)
from netconfpkg.gdt import Gdtlist, gdtlist_properties


class IPsecList_base(Gdtlist):
    gdtlist_properties(IPsec)

class IPsecList(IPsecList_base):
    def __init__(self):
        super(IPsecList, self).__init__()
        self.oldname = None

    def load(self):
        from netconfpkg.NCIPsec import ConfIPsec
        
        self.__delslice__(0, len(self))

        devices = ConfDevices()
        for ipsec_name in devices:
            conf = ConfIPsec(ipsec_name)
            mtype = None
            # take a peek in the config file
            if conf.has_key("TYPE"):
                mtype = conf["TYPE"]

            if mtype != "IPSEC":
                continue

            log.log(5, "Loading ipsec config %s" % ipsec_name)
            ipsec = IPsec()
            ipsec.load(ipsec_name)
            self.append(ipsec)

        self.commit()
        self.setunmodified()

    def save(self):
        
        from netconfpkg.NCIPsec import ConfIPsec
        for ipsec in self:
            ipsec.save()

        self.commit()

        dirname = getRoot() + SYSCONFDEVICEDIR
        #
        # Remove old config files
        #
        try:
            mdir = os.listdir(dirname)
        except OSError, msg:
            raise IOError, 'Cannot save in ' \
                  + dirname + ': ' + str(msg)
        for entry in mdir:
            if not testFilename(dirname + entry):
                continue

            if (len(entry) <= 6) or \
                   entry[:6] != 'ifcfg-':
                continue

            ipsecid = entry[6:]

            for ipsec in self:
                if ipsec.IPsecId == ipsecid:
                    break
            else:
                # check for IPSEC
                conf = ConfIPsec(ipsecid)
                mtype = None
                if conf.has_key("TYPE"): 
                    mtype = conf["TYPE"]
                if mtype != IPSEC:
                    continue

                unlink(dirname + entry)
                unlink(getRoot() + OLDSYSCONFDEVICEDIR + \
                       '/ifcfg-' + ipsecid)

        #
        # Remove old key files
        #
        try:
            mdir = os.listdir(dirname)
        except OSError, msg:
            raise IOError, 'Cannot save in ' \
                  + dirname + ': ' + str(msg)
        for entry in mdir:
            if not testFilename(dirname + entry):
                continue

            if (len(entry) <= 5) or \
               entry[:5] != 'keys-':
                continue

            ipsecid = entry[5:]

            for ipsec in self:
                if ipsec.IPsecId == ipsecid:
                    break
            else:
                # check for IPSEC
                from netconfpkg.NCDevice import ConfDevice
                conf = ConfDevice(ipsecid)
                mtype = None
                if conf.has_key("TYPE"): 
                    mtype = conf["TYPE"]
                if mtype:
                    continue

                unlink(dirname + entry)
                unlink(getRoot() + OLDSYSCONFDEVICEDIR+'/keys-'+ipsecid)

        self.commit()
        self.setunmodified()

    def __repr__(self):
        return repr(self.__dict__)

    def _objToStr(self, parentStr = None): # pylint: disable-msg=W0613
        retstr = ""
        for ipsec in self:
            # pylint: disable-msg=W0212
            retstr += ipsec._objToStr("IPsecList.%s" % (ipsec.IPsecId))

        return retstr

    def fromstr(self, vals, value):
        # pylint: disable-msg=W0212
        if len(vals) <= 1:
            return
        if vals[0] == "IPsecList":
            del vals[0]
        else:
            return

        for ipsec in self:
            if ipsec.IPsecId == vals[0]:
                ipsec.fromstr(vals[1:], value)
                return

        ipsec = IPsec(vals[0])
        self.append(ipsec)
        ipsec.fromstr(vals[1:], value)


__IPSList = None

def getIPsecList(refresh = None):
    # pylint: disable-msg=W0603
    global __IPSList
    if __IPSList == None or refresh:
        __IPSList = IPsecList()
        __IPSList.load()
    return __IPSList
