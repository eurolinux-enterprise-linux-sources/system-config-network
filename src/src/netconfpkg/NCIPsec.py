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
import netconfpkg
import os
from netconfpkg.NC_functions import (_, getRoot, SYSCONFDEVICEDIR, 
                                     generic_run_dialog,
                                     bits_to_netmask, ConfKeys,
                                     netmask_to_bits, rename)
from netconfpkg.conf import ConfShellVar
from netconfpkg.gdt import (Gdtstruct, gdtstruct_properties, Gdtstr, Gdtbool)


class IPsec_base(Gdtstruct):
    gdtstruct_properties([
                          ('IPsecId', Gdtstr, "Test doc string"),
                          ('Address', Gdtstr, "Test doc string"),
                          ('ConnectionType', Gdtstr, "Test doc string"),
                          ('EncryptionMode', Gdtstr, "Test doc string"),
                          ('LocalNetwork', Gdtstr, "Test doc string"),
                          ('LocalNetmask', Gdtstr, "Test doc string"),
                          ('LocalGateway', Gdtstr, "Test doc string"),
                          ('RemoteNetwork', Gdtstr, "Test doc string"),
                          ('RemoteNetmask', Gdtstr, "Test doc string"),
                          ('RemoteGateway', Gdtstr, "Test doc string"),
                          ('RemoteIPAddress', Gdtstr, "Test doc string"),
                          ('SPI_AH_IN', Gdtstr, "Test doc string"),
                          ('SPI_AH_OUT', Gdtstr, "Test doc string"),
                          ('SPI_ESP_IN', Gdtstr, "Test doc string"),
                          ('SPI_ESP_OUT', Gdtstr, "Test doc string"),
                          ('AHKey', Gdtstr, "Test doc string"),
                          ('ESPKey', Gdtstr, "Test doc string"),
                          ('IKEKey', Gdtstr, "Test doc string"),
                          ('OnBoot', Gdtbool, "Test doc string"),
                          ])
    
    def __init__(self):
        super(IPsec_base, self).__init__()
        self.IPsecId = None
        self.Address = None
        self.ConnectionType = None
        self.EncryptionMode = None
        self.LocalNetwork = None
        self.LocalNetmask = None
        self.LocalGateway = None
        self.RemoteNetwork = None
        self.RemoteNetmask = None
        self.RemoteGateway = None
        self.RemoteIPAddress = None
        self.SPI_AH_IN = None
        self.SPI_AH_OUT = None
        self.SPI_ESP_IN = None
        self.SPI_ESP_OUT = None
        self.AHKey = None
        self.ESPKey = None
        self.IKEKey = None
        self.OnBoot = None
        
    
class ConfIPsec(ConfShellVar.ConfShellVar):
    def __init__(self, name):
        ConfShellVar.ConfShellVar.__init__(self, getRoot() 
                                           + SYSCONFDEVICEDIR 
                                           + 'ifcfg-' + name)
        self.chmod(0644)

class IPsec(IPsec_base):
    keyid = "IPsecId"

    boolkeydict = {
        'OnBoot' : 'ONBOOT', 
        }
    ipsec_entries = {
        "LocalNetwork" : "SRCNET", 
        "LocalGateway" : "SRCGW", 
        "RemoteNetwork" : "DSTNET", 
        "RemoteGateway" : "DSTGW", 
        "RemoteIPAddress" : "DST", 
        "OnBoot" : "ONBOOT", 
        "SPI_AH_IN" : "SPI_AH_IN", 
        "SPI_AH_OUT" : "SPI_AH_OUT", 
        "SPI_ESP_IN" : "SPI_ESP_IN", 
        "SPI_ESP_OUT" : "SPI_ESP_OUT", 
        }
    key_entries = {
        "AHKey" : "KEY_AH", 
        "ESPKey" : "KEY_ESP", 
        "IKEKey" : "IKE_PSK", 
        }

    def __init__(self):
        super(IPsec, self).__init__()
        self.oldname = None

    def load(self, name):
        # load ipsec
        # pylint: disable-msg=W0201
        conf = ConfIPsec(name)
        for selfkey in self.ipsec_entries.keys():
            confkey = self.ipsec_entries[selfkey]
            if conf.has_key(confkey):
                setattr(self, selfkey, conf[confkey] or None)

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if conf.has_key(confkey):
                if conf[confkey] == 'yes':
                    setattr(self, selfkey, True)
                else:
                    setattr(self, selfkey, False)
            elif not self.__dict__.has_key(selfkey):
                setattr(self, selfkey, False)

        conf = ConfKeys(name)
        for selfkey in self.key_entries.keys():
            confkey = self.key_entries[selfkey]
            if conf.has_key(confkey):
                setattr(self, selfkey, conf[confkey] or None)

        if conf.has_key("IKE_PSK") and conf["IKE_PSK"]:
            self.EncryptionMode = "auto"
        else:
            self.EncryptionMode = "manual"

        if not self.IPsecId:
            self.IPsecId = name

        if self.LocalNetwork:
            vals = self.LocalNetwork.split("/")
            if len(vals) >= 1:
                self.LocalNetwork = vals[0]
                self.LocalNetmask = bits_to_netmask(vals[1])

        if self.RemoteNetwork:
            vals = self.RemoteNetwork.split("/")
            if len(vals) >= 1:
                self.RemoteNetwork = vals[0]
                self.RemoteNetmask = bits_to_netmask(vals[1])
            self.ConnectionType = "Net2Net"
        else:
            self.ConnectionType = "Host2Host"

        self.oldname = self.IPsecId

        self.commit() 
        self.setunmodified()

    def save(self):
        # FIXME: [163040] "Exception Occurred" when saving
        # fail gracefully, with informing, which file, and why

        # Just to be safe...
        os.umask(0022)
        self.commit() 

        if self.oldname and (self.oldname != self.IPsecId):
            for prefix in [ 'ifcfg-', 'keys-' ]:
                rename(getRoot() + SYSCONFDEVICEDIR + \
                       prefix + self.oldname, 
                       getRoot() + SYSCONFDEVICEDIR + \
                       prefix + self.IPsecId)

        # save ipsec settings
        conf = ConfIPsec(self.IPsecId)
        conf.fsf()
        conf["TYPE"] = "IPSEC"
        conf["DST"] = self.RemoteIPAddress 

        if self.ConnectionType == "Net2Net":
            conf["SRCNET"] = self.LocalNetwork + "/" + \
                             str(netmask_to_bits(self.LocalNetmask))
            conf["DSTNET"] = self.RemoteNetwork + "/" + \
                             str(netmask_to_bits(self.RemoteNetmask))
            conf["SRCGW"] = self.LocalGateway 
            conf["DSTGW"] = self.RemoteGateway 
        else:
            for key in ["SRCNET", "DSTNET", "SRCGW", "DSTGW"]:
                del conf[key]

        if self.EncryptionMode == "auto":
            conf["IKE_METHOD"] = "PSK"
        else:
            del conf["IKE_METHOD"]
            spi_entries = { "SPI_AH_IN" : "SPI_AH_IN", 
                            "SPI_AH_OUT" : "SPI_AH_OUT", 
                            "SPI_ESP_IN" : "SPI_ESP_IN", 
                            "SPI_ESP_OUT" : "SPI_ESP_OUT" }

            for selfkey in spi_entries.keys():
                confkey = spi_entries[selfkey]
                if hasattr(self, selfkey):
                    conf[confkey] = getattr(self, selfkey)
                else: conf[confkey] = ""


        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if hasattr(self, selfkey):
                conf[confkey] = 'yes'
            else:
                conf[confkey] = 'no'

        conf.write()

        conf = ConfKeys(self.IPsecId)
        conf.fsf()
        for selfkey in self.key_entries.keys():
            confkey = self.key_entries[selfkey]
            if hasattr(self, selfkey):
                conf[confkey] = getattr(self, selfkey)
            else: del conf[confkey]

        conf.write()

        #
        self.oldname = self.IPsecId

    def activate(self, dialog = None):
        command = '/sbin/ifup'
        param = [command, self.IPsecId, "up"]

        try:
            (ret, msg) =  generic_run_dialog(\
                command, 
                param, 
                catchfd = (1, 2), 
                title = _('IPsec activating...'), 
                label = _('Activating IPsec connection %s, '
                          'please wait...') % (self.IPsecId), 
                errlabel = _('Cannot activate '
                             'IPsec connection %s!\n') % (self.IPsecId), 
                dialog = dialog)

        except RuntimeError, msg:
            ret = -1

        return ret, msg

    def deactivate(self, dialog = None):
        command = '/sbin/ifdown'
        param = [command, self.IPsecId, "down"]

        try:
            (ret, msg) = generic_run_dialog(\
                command, param, 
                catchfd = (1, 2), 
                title = _('IPsec deactivating...'), 
                label = _('Deactivating IPsec connection %s, '
                          'please wait...') % (self.IPsecId), 
                errlabel = _('Cannot deactivate '
                             'IPsec connection %s!\n') % (self.IPsecId), 
                dialog = dialog)

        except RuntimeError, msg:
            ret = -1

        return ret, msg

netconfpkg.IPsec = IPsec
