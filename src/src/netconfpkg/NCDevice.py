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
import re
from netconfpkg import NC_functions
from netconfpkg.NCRoute import Route
from netconfpkg.NC_functions import (_, getRoot, SYSCONFDEVICEDIR, log, 
                                     ETHERNET, SYSCONFNETWORK, 
                                     generic_run_dialog, generic_run, 
                                     getDebugLevel, unlink)
from netconfpkg.conf import ConfShellVar
from netconfpkg.gdt import (Gdtstruct, gdtstruct_properties, Gdtstr, 
                            Gdtlist, Gdtbool, Gdtint, gdtlist_properties)


class StaticRoutes(Gdtlist):
    "Contains Routes"
    gdtlist_properties(Route)

class Device_base(Gdtstruct):
    gdtstruct_properties([
                          ('DeviceId', Gdtstr, "Test doc string"),
                          ('NMControlled', Gdtbool, "Test doc string"),
                          ('Device', Gdtstr, "Test doc string"),
                          ('Alias', Gdtint, "Test doc string"),
                          ('Type', Gdtstr, "Test doc string"),
                          ('SubType', Gdtstr, "Test doc string"),
                          ('OnBoot', Gdtbool, "Test doc string"),
                          ('OnParent', Gdtbool, "Test doc string"),
                          ('AllowUser', Gdtbool, "Test doc string"),
                          ('BootProto', Gdtstr, "Test doc string"),
                          ('IP', Gdtstr, "Test doc string"),
                          ('Netmask', Gdtstr, "Test doc string"),
                          ('Gateway', Gdtstr, "Test doc string"),
                          ('IPv6Init', Gdtbool, "Test doc string"),
                          ('Hostname', Gdtstr, "Test doc string"),
                          ('Domain', Gdtstr, "Test doc string"),
                          ('AutoDNS', Gdtbool, "Test doc string"),
                          ('HardwareAddress', Gdtstr, "Test doc string"),
                          ('Mtu', Gdtint, "Test doc string"),
                          ('Slave', Gdtbool, "Test doc string"),
                          ('StaticRoutes', StaticRoutes, "test"),
                          ('PrimaryDNS', Gdtstr, "Test doc string"),
                          ('SecondaryDNS', Gdtstr, "Test doc string"),
                          ])
    

    
    def __init__(self):
        super(Device_base, self).__init__()
        self.DeviceId = None
        self.NMControlled = None
        self.Device = None
        self.Alias = None
        self.Type = None
        self.SubType = None
        self.OnBoot = None
        self.OnParent = None
        self.AllowUser = None
        self.BootProto = None
        self.IP = None
        self.Netmask = None
        self.Gateway = None
        self.IPv6Init = None
        self.Hostname = None
        self.Domain = None
        self.AutoDNS = None
        self.HardwareAddress = None
        self.Mtu = None
        self.Slave = None
        self.StaticRoutes = None
        self.PrimaryDNS = None
        self.SecondaryDNS = None

    def createStaticRoutes(self):
        if not self.StaticRoutes:
            self.StaticRoutes = StaticRoutes()
        return self.StaticRoutes
                          
# pylint: disable-msg=W0201

class ConfDevice(ConfShellVar.ConfShellVar):
    def __init__(self, name, mdir = None):
        if mdir == None:
            mdir = getRoot() + SYSCONFDEVICEDIR
        new = False
        self.filename = mdir + 'ifcfg-' + name
        if not os.access(self.filename, os.R_OK):
            new = True
            self.oldmode = 0644
        else:
            status = os.stat(self.filename)
            self.oldmode = status[0]
            #print status

        ConfShellVar.ConfShellVar.__init__(self, self.filename)

        if new:
            self.rewind()
            self.insertline( "# Please read /usr/share/doc/"
                            "initscripts-*/sysconfig.txt" )
            self.nextline()
            self.insertline("# for the documentation of these parameters.")
            self.rewind()

    def write(self):
        self.chmod(self.oldmode)
        log.log(2, "chmod %#o %s" % (self.oldmode & 03777, self.filename) )
        #if ((self.oldmode & 0044) != 0044):
        #    ask = NC_functions.generic_yesno_dialog(\
        #        _("May I change\n%s\nfrom mode %o to %o?") % \
        #        (self.filename, self.oldmode & 03777, 0644))
        #    if ask != RESPONSE_YES:
        #        self.chmod(self.oldmode)
        ConfShellVar.ConfShellVar.write(self)

class ConfRoute(ConfShellVar.ConfShellVar):
    def __init__(self, name):
        ConfShellVar.ConfShellVar.__init__(self, getRoot() 
                                            + SYSCONFDEVICEDIR
                                            + 'route-' + name)
        self.chmod(0644)

# FIXME: [157630] system-config-networks needs options 
# for setting default route and metric
class Device(Device_base):
    Type = ETHERNET
    SubType = None
    Priority = 0
    keyid = "DeviceId"
    
    __keydict = { 
                 'Device' : 'DEVICE',
                 'IP' : 'IPADDR',
                 'Netmask' : 'NETMASK',
                 'Gateway' : 'GATEWAY',
                 'Hostname' : 'DHCP_HOSTNAME',
                 'PrimaryDNS' : 'DNS1',
                 'SecondaryDNS' : 'DNS2',
                 'Domain' : 'DOMAIN',
                 'BootProto' : 'BOOTPROTO',
                 'Type' : 'TYPE',
                 'HardwareAddress' : 'HWADDR',
                 }

    __intkeydict = {
                    'Mtu' : 'MTU', 
                    }


    __boolkeydict = { 
                     'OnBoot' : 'ONBOOT',
                     'OnParent' : 'ONPARENT',
                     'NMControlled' : 'NM_CONTROLLED',
                     'AllowUser' : 'USERCTL',
                     'AutoDNS' : 'PEERDNS',
                     'Slave' : 'SLAVE',
                     'IPv6Init' : 'IPV6INIT',
                     }

    def __init__(self):
        super(Device, self).__init__()
        self.oldname = None
        
    def getDialog(self):
	return None

    def getWizard(self):
	return None

    def isType(self, device):
        raise False

    def testDeviceId(self, value):
        if re.search(r"^[a-z|A-Z|0-9\_:]+$", value):
            return True
        return False

    def getDeviceAlias(self):
        devname = self.Device
        if self.Alias != None and self.Alias != "":
            devname = devname + ':' + str(self.Alias)
        return devname
    
    def getRealMtu(self):
        out = commands.getoutput('/sbin/ip link show %s 2>/dev/null'
                                 % self.Device)
        next = False
        val = 0
        try:
            for k in out.split():
                if next: 
                    val = int(k)
                    break
                if k == "mtu": 
                    next = True
        except ValueError:
            pass
        
        return val

    def load(self, name):
    
        conf = ConfDevice(name)

        self.oldname = name

        if not conf.has_key("DEVICE"):
            aliaspos = name.find(':' )
            if aliaspos != -1:
                from netconfpkg.NCDeviceList import getDeviceList
                # ok, we have to inherit all other data from our master
                for dev in getDeviceList():
                    if dev.Device == name[:aliaspos]:
                        self.apply(dev) 
                        break

            self.Device = name

        self.DeviceId = name
        for selfkey in self.__keydict.keys():
            confkey = self.__keydict[selfkey]
            if conf.has_key(confkey) and conf[confkey]:
                setattr(self, selfkey, conf[confkey])
                #setattr(self, selfkey, conf[confkey])

        for selfkey in self.__intkeydict.keys():
            confkey = self.__intkeydict[selfkey]
            if conf.has_key(confkey) and len(conf[confkey]):
                setattr(self, selfkey, conf[confkey])
                #setattr(self, selfkey, int(conf[confkey]))

        for selfkey in self.__boolkeydict.keys():
            confkey = self.__boolkeydict[selfkey]
            if conf.has_key(confkey):
                if conf[confkey] == 'yes':
                    setattr(self, selfkey, True)
                    #print >> sys.stderr, self.DeviceId, selfkey, "True"
                    #setattr(self, selfkey, True)
                else:
                    setattr(self, selfkey, False)
                    #print >> sys.stderr, self.DeviceId, selfkey, "False"
                    #setattr(self, selfkey, False)
            # we need to deal with options which have default value 'yes' like NM_CONTROLLED
            else:
                if confkey != "NM_CONTROLLED":
                    setattr(self, selfkey, False)
                #setattr(self, selfkey, False)

        if not conf.has_key("PEERDNS"):
            del self.AutoDNS

        if not self.Slave:
            del self.Slave

        if not self.Gateway:
            try:
                cfg = ConfShellVar.ConfShellVar(getRoot() + SYSCONFNETWORK )
                if (cfg.has_key('GATEWAY') 
                    and ((not cfg.has_key('GATEWAYDEV')) 
                          or cfg['GATEWAYDEV'] == self.Device)):
                    gw = cfg['GATEWAY']

                    if gw and self.Netmask:
                        try:
                            network = commands.getoutput( 'ipcalc --network '+
                                                         str(self.IP) + 
                                                         ' ' + 
                                                         str(self.Netmask) +
                                                         ' 2>/dev/null' )

                            out = commands.getoutput( 'ipcalc --network ' + 
                                                     str(gw) + ' ' 
                                                     + str(self.Netmask) + 
                                                     ' 2>/dev/null' )
                            if out == network:
                                self.Gateway = str(gw)
                        except:
                            pass


            except EnvironmentError, msg:
                NC_functions.generic_error_dialog(str(msg) )

        try:
            aliaspos = self.Device.find(':' )
            if aliaspos != -1:
                self.Alias = int(self.Device[aliaspos+1:])
                self.Device = self.Device[:aliaspos]
        except TypeError:
            NC_functions.generic_error_dialog( _( "%s, "
                                                "Device not specified "
                                                "or alias not a number!" ) 
                                              % self.DeviceId )
            #raise TypeError, _("Device not specified or alias not a number!")
        except ValueError:
            NC_functions.generic_error_dialog( _( "%s, "
                                                "Device not specified "
                                                "or alias not a number!" ) 
                                                % self.DeviceId )

        if not self.Alias:
            del self.OnParent

        if self.BootProto == None:
            if self.IP:
                self.BootProto = "none"
            else:
                self.BootProto = 'dhcp'

        if not self.Type or self.Type == "" or self.Type == _("Unknown"):
            from netconfpkg import NCHardwareList
            hwlist = NCHardwareList.getHardwareList()
            for hw in hwlist:
                if hw.Name == self.Device:
                    self.Type = hw.Type
                    break
            else:
                self.Type = NC_functions.getDeviceType(self.Device)

        if conf.has_key("RESOLV_MODS"):
            if conf["RESOLV_MODS"] != "no":
                self.AutoDNS = True
            else:
                self.AutoDNS = False

        # move old <id>.route files to route-<id>
        mfile = str(getRoot() + SYSCONFDEVICEDIR +
                                self.DeviceId + '.route')
        if os.path.isfile(mfile):
            NC_functions.rename(mfile,
                                getRoot() + SYSCONFDEVICEDIR +
                                'route-' + self.DeviceId )
        # load routes
        rconf = ConfRoute(name)

        for key in rconf.keys():
            if key.startswith("ADDRESS"):
                try:
                    p = int(key[7:])
                except:
                    continue
                route = Route()

                self.createStaticRoutes() 
                self.StaticRoutes.append(route)
                   
                route.Address = rconf['ADDRESS' + str(p)]                
                if rconf.has_key("NETMASK" + str(p)):
                    route.Netmask = rconf['NETMASK' + str(p)]
                if rconf.has_key("GATEWAY" + str(p)):
                    route.Gateway = rconf['GATEWAY' + str(p)]
                
        self.commit() 
        self.setunmodified()

    def save(self):
        # FIXME: [163040] "Exception Occurred" when saving
        # fail gracefully, with informing, which file, and why

        # Just to be safe...
        os.umask(0022)
        self.commit() 

        if self.oldname and (self.oldname != self.DeviceId):
            for prefix in [ 'ifcfg-', 'route-', 'keys-' ]:
                NC_functions.rename(getRoot() + SYSCONFDEVICEDIR + 
                                    prefix + self.oldname,
                                    getRoot() + SYSCONFDEVICEDIR +
                                    prefix + self.DeviceId )

        conf = ConfDevice(self.DeviceId)
        conf.fsf()

        if self.BootProto == None:
            if self.IP:
                self.BootProto = "none"
            else:
                self.BootProto = 'dhcp'

        if self.BootProto:
            self.BootProto = self.BootProto.lower()

        if self.BootProto == "static":
            self.BootProto = "none"

        # Do not set GATEWAY with dhcp
        if self.BootProto == 'dhcp':
            # [169526] lost Gateway when I change static IP by DHCP
            # #167593, #162902, #169113, #149780
            self.Gateway = None
            self.IP = None
            self.Netmask = None

        for selfkey in self.__keydict.keys():
            confkey = self.__keydict[selfkey]
            if hasattr(self, selfkey):
                conf[confkey] = getattr(self, selfkey)
            else: conf[confkey] = ""

        for selfkey in self.__intkeydict.keys():
            confkey = self.__intkeydict[selfkey]
            if hasattr(self, selfkey) and getattr(self, selfkey) != None:
                conf[confkey] = str(getattr(self, selfkey))
            else: del conf[confkey]

        for selfkey in self.__boolkeydict.keys():
            confkey = self.__boolkeydict[selfkey]
            if getattr(self, selfkey) == True:
                conf[confkey] = 'yes'
            elif getattr(self, selfkey) == False:
                conf[confkey] = 'no'
            else: del conf[confkey]

        # cleanup
        if self.Alias != None:
            # FIXME: [167991] Add consistency check for aliasing
            # check, if a parent device exists!!!
            conf['DEVICE'] = str(self.Device) + ':' + str(self.Alias)
            del conf['ONBOOT']
            # Alias interfaces should not have a HWADDR (bug #188321, #197401)
            del conf['HWADDR']
        else:
            del conf['ONPARENT']

        # Recalculate BROADCAST and NETWORK values if IP and netmask are
        # present (#51462)
        # obsolete
        if self.IP and self.Netmask and conf.has_key('BROADCAST'):
            try:
                broadcast = commands.getoutput( 'ipcalc --broadcast ' + 
                                               str(self.IP) + 
                                               ' ' + str(self.Netmask) + 
                                               ' 2>/dev/null' )
                if broadcast:
                    conf['BROADCAST'] = broadcast[10:]
            except:
                pass
        else:
            del conf['BROADCAST']

        if self.IP and self.Netmask and conf.has_key('NETWORK'):
            try:
                network = commands.getoutput( 'ipcalc --network ' + 
                                             str(self.IP) + 
                                             ' ' + str(self.Netmask) + 
                                             ' 2>/dev/null' )
                if network:
                    conf['NETWORK'] = network[8:]
            except:
                pass
        else:
            del conf['NETWORK']
            
        # FIXME: RFE [174974] limitation of setting routing
        if self.StaticRoutes and len(self.StaticRoutes) > 0: 
            rconf = ConfRoute(self.DeviceId)
            for key in rconf.keys():
                del rconf[key]
            p = 0
            for route in self.StaticRoutes:
                if route.Address:
                    rconf['ADDRESS'+str(p)] = route.Address
                if route.Netmask:
                    rconf['NETMASK'+str(p)] = route.Netmask
                if route.Gateway:
                    rconf['GATEWAY'+str(p)] = route.Gateway
                p = p + 1
            rconf.write()
        else:
            # remove route file, if no routes defined
            unlink(getRoot() + SYSCONFDEVICEDIR + self.DeviceId + '.route' )
            unlink(getRoot() + SYSCONFDEVICEDIR + 'route-' + self.DeviceId )

        # remove empty gateway entries
        if not self.Gateway:
            del conf['GATEWAY']


        for i in conf.keys():
            if not conf[i] or conf[i] == "":
                del conf[i]

        # RESOLV_MODS should be PEERDNS
        if conf.has_key('RESOLV_MODS'):
            del conf['RESOLV_MODS']

        conf.write()

        self.oldname = self.DeviceId

    def activate(self, dialog = None):
        command = '/sbin/ifup'
        param = [command, self.DeviceId, "up"]

        try:
            (ret, msg) =  generic_run_dialog( \
                command,
                param,
                catchfd = (1, 2),
                title = _('Network device activating...'),
                label = _( 'Activating network device %s, '
                          'please wait...' ) % (self.DeviceId),
                errlabel = _( 'Cannot activate '
                             'network device %s!\n' ) % (self.DeviceId),
                dialog = dialog )

        except RuntimeError, msg:
            ret = -1

        return ret, msg

    def deactivate(self, dialog = None):
        command = '/sbin/ifdown'
        param = [command, self.DeviceId, "down"]

        try:
            (ret, msg) = generic_run_dialog( 
                command, param,
                catchfd = (1, 2),
                title = _('Network device deactivating...'),
                label = _( 'Deactivating network device %s, '
                          'please wait...' ) % (self.DeviceId),
                errlabel = _( 'Cannot deactivate '
                             'network device %s!\n' ) % (self.DeviceId),
                dialog = dialog )

        except RuntimeError, msg:
            ret = -1

        return ret, msg

    def configure(self):
        command = '/usr/bin/system-config-network'
        args = ''
        if not os.path.isfile(command) and getDebugLevel() > 0:
            command = os.getcwd() + '/system-config-network-gui'
            args = '-d'

        try:
            (ret, msg) =  generic_run( command,
                                      [command, args],
                                      catchfd = (1, 2) )
        except RuntimeError, msg:
            ret = -1

        return ret, msg

    def monitor(self):
        pass

    def getHWDevice(self):
        return self.Device

__author__ = "Harald Hoyer <harald@redhat.com>"
