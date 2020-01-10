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
import os
import re
from netconfpkg.gui import GUI_functions


## FIXME: ...
provider_db = "providerdb"
if not os.path.exists(provider_db):
    provider_db = "netconfpkg/" + "providerdb"
if not os.path.exists(provider_db):
    provider_db = GUI_functions.NETCONFDIR + "providerdb"
if not os.path.exists(provider_db):
    provider_db = GUI_functions.NETCONFDIR + "netconfpkg/" + "providerdb"

class provider:
    def __init__(self):
        self.provider_data = []
        self.clear()

    def clear(self):
        # pylint: disable-msg=W0201
        self.country = ""
        self.city = ""
        self.flag = ""
        self.name = ""
        self.connection_type = ""
        self.user_name = ""
        self.password = ""
        self.areacode = ""
        self.phone = ""
        self.domain = ""
        self.dns = ""
        self.netmask = ""
        self.encap = ""
        self.layer = ""
        self.auth_type = ""
        self.ip_mode = ""

    def get_country(self):
        return self.country

    def set_country(self, country):
        self.country = country

    def get_city(self):
        return self.city

    def set_city(self, city):
        self.city = city

    def get_flag(self):
        return self.flag

    def set_flag(self, flag):
        self.flag = flag

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_connection_type(self):
        return self.connection_type

    def set_connection_type(self, connection_type):
        self.connection_type = connection_type

    def get_user_name(self):
        return self.user_name

    def set_user_name(self, user_name):
        self.user_name = user_name

    def get_password(self):
        return self.password

    def set_password(self, password):
        self.password = password

    def get_areacode(self):
        return self.areacode

    def set_areacode(self, areacode):
        self.areacode = areacode

    def get_phone(self):
        return self.phone

    def set_phone(self, phone):
        self.phone = phone

    def get_domain(self):
        return self.domain

    def set_domain(self, domain):
        self.domain = domain

    def get_dns(self):
        return self.dns

    def set_dns(self, dns):
        self.dns = dns

    def get_netmask(self):
        return self.netmask

    def set_netmask(self, netmask):
        self.netmask = netmask

    def get_encap(self):
        return self.encap

    def set_encap(self, encap):
        self.encap = encap

    def get_layer(self):
        return self.layer

    def set_layer(self, layer):
        self.layer = layer

    def get_auth_type(self):
        return self.auth_type

    def set_auth_type(self, auth_type):
        self.auth_type = auth_type

    def get_ip_mode(self):
        return self.ip_mode

    def set_ip_mode(self, ip_mode):
        self.ip_mode = ip_mode

    def get_provider_data(self):
        self.provider_data = {'Country' : self.country,
                              'City' : self.city,
                              'Flag' : self.flag,
                              'ProviderName' : self.name,
                              'ConnectionType' : self.connection_type,
                              'Login': self.user_name,
                              'Password' : self.password,
                              'Areacode' : self.areacode,
                              'PhoneNumber' : self.phone,
                              'Domain' : self.domain,
                              'DNS' : self.dns,
                              'Netmask' : self.netmask,
                              'EncapMode': self.encap,
                              'Layer2' : self.layer,
                              'Authentication': self.auth_type,
                              'IpMode' : self.ip_mode }

        return self.provider_data

def get_value(s):
    s = s.split(" ", 1)
    return s[1].strip()

def get_provider_list(Type="isdn"):
    db_list = []
    if not os.path.exists(provider_db):
        return db_list

    mdb = open(provider_db, "r")
    line = mdb.readline()
    Type = Type.lower()

    while line:
        line = line.strip()
        if len(line) == 0 or line[0] == "#":
            line = mdb.readline()
            continue

        if line[:7] != "[Begin]":
            print "error: expect [Begin]"
            return db_list

        isp = provider()

        while line[:5] != "[End]":
            line = line.strip()
            if line[:9] == "[Country]":
                isp.set_country(get_value(line))
            elif line[:6] == "[Flag]":
                isp.set_flag(get_value(line))
            elif line[:6] == "[City]":
                isp.set_city(get_value(line))
            elif line[:6] == "[Name]":
                isp.set_name(get_value(line))
            elif line[:6] == "[Type]":
                isp.set_connection_type(get_value(line))
            elif line[:6] == "[User]":
                isp.set_user_name(get_value(line))
            elif line[:6] == "[Pass]":
                isp.set_password(get_value(line))
            elif line[:8] == "[Prefix]":
                isp.set_areacode(get_value(line))
            elif line[:7] == "[Phone]":
                isp.set_phone(get_value(line))
            elif line[:8] == "[Domain]":
                isp.set_domain(get_value(line))
            elif line[:5] == "[DNS]":
                isp.set_dns(get_value(line))
            elif line[:9] == "[Netmask]":
                isp.set_netmask(get_value(line))
            elif line[:8] == "[Encaps]":
                isp.set_encap(get_value(line))
            elif line[:8] == "[Layer2]":
                isp.set_layer(get_value(line))
            elif line[:6] == "[Auth]":
                isp.set_auth_type(get_value(line))
            elif line[:9] == "[Ipsetup]":
                isp.set_ip_mode(get_value(line))
            line = mdb.readline()

        if re.search(Type, isp.get_connection_type()):
            isp.set_connection_type(Type)
            db_list.append(isp.get_provider_data())
        line = mdb.readline()

    mdb.close()

    return db_list

if __name__ == "__main__":
    a = get_provider_list("modem")
    for db in a:
        print db

__author__ = "Than Ngo <than@redhat.com>"

