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
from netconfpkg.NCCallback import Callback
from netconfpkg.NCCompression import Compression
from netconfpkg.NC_functions import (_, getRoot, log, unlink, getCHAPConf,
                                     getPAPConf, WVDIALCONF, mkdir, PPPDIR)
from netconfpkg.conf import ConfSMB
from netconfpkg.gdt import (Gdtstruct, gdtstruct_properties,
                            Gdtstr, Gdtlist, Gdtbool, Gdtint,
                            gdtlist_properties)
from netconfpkg import NCHardwareList


class PPPOption(Gdtstr):
    pass

class PPPOptions(Gdtlist):
    gdtlist_properties(PPPOption)

class Dialup_base(Gdtstruct):
    "Dialup structure"
    gdtstruct_properties([
                          ('Hostname', Gdtstr, "Test doc string"),
                          ('ProviderName', Gdtstr, "Test doc string"),
                          ('Login', Gdtstr, "Test doc string"),
                          ('Password', Gdtstr, "Test doc string"),
                          ('Authentication', Gdtstr, "Test doc string"),
                          ('MSN', Gdtstr, 'VALUE="0"'),
                          ('Prefix', Gdtstr, "Test doc string"),
                          ('Areacode', Gdtstr, "Test doc string"),
                          ('Regioncode', Gdtstr, "Test doc string"),
                          ('PhoneNumber', Gdtstr, "Test doc string"),
                          ('LocalIP', Gdtstr, "Test doc string"),        
                          ('RemoteIP', Gdtstr, "Test doc string"),        
                          ('Persist', Gdtbool, "Test doc string"),
                          ('DefRoute', Gdtbool, "Test doc string"),
                          ('Inherits', Gdtstr, "Test doc string"),
                          ('ChargeHup', Gdtstr, "Test doc string"),
                          ('ChargeInt', Gdtstr, "Test doc string"),
                          ('Ihup', Gdtstr, "Test doc string"),
                          ('DialMax', Gdtint, 'VALUE="3"'),
                          ('Layer2', Gdtstr, 'VALUE="hdlc"'),
                          ('Layer3', Gdtstr, 'VALUE="trans"'),
                          ('Mru', Gdtint, 'VALUE="0"'),
                          ('PPPOptions', PPPOptions, "Test doc string"),
                          ('StupidMode', Gdtbool, "Test doc string"),
                          ('DialinServer', Gdtbool, "Test doc string"),
                          ('ChannelBundling', Gdtbool, "Test doc string"),
                          ('EncapMode', Gdtstr, "Test doc string"),
                          ('HangupTimeout', Gdtint, 'VALUE="600"'),
                          ('DialMode', Gdtstr, 'VALUE="manual"'),
                          ('SlaveDevice', Gdtstr, "Test doc string"),
                          ('EthDevice', Gdtstr, "Test doc string"),    
                          ('ServiceName', Gdtstr, "Test doc string"),    
                          ('AcName', Gdtstr, "Test doc string"),    
                          ('SyncPPP', Gdtbool, "Test doc string"),    
                          ('InitString', Gdtstr, "Test doc string"),
                          ('Secure', Gdtbool, "Test doc string"),
                          ('PhoneInNumber', Gdtstr, "Test doc string"),
                          ('Callback', Callback,  "Test doc string"),
                          ('Compression', Compression, "Test doc string"),
                          ])

    def __init__(self):
        super(Dialup_base, self).__init__()
        self.Hostname = None
        self.ProviderName = None
        self.Login = None
        self.Password = None
        self.Authentication = None
#        self.MSN = "0"
        self.MSN = None
        self.Prefix = None
        self.Areacode = None
        self.Regioncode = None
        self.PhoneNumber = None
        self.LocalIP = None        
        self.RemoteIP = None        
        self.Persist = None
        self.DefRoute = None
        self.Inherits = None
        self.ChargeHup = None
        self.ChargeInt = None
        self.Ihup = None
#        self.DialMax = "3"
        self.DialMax = None
#        self.Layer2 = "hdlc"
        self.Layer2 = None
#        self.Layer3 = "trans"
        self.Layer3 = None
        self.Mru = None
        self.PPPOptions = PPPOptions()
        self.StupidMode = None
        self.DialinServer = None
        self.ChannelBundling = None
        self.EncapMode = None
        self.HangupTimeout = 600
#        self.HangupTimeout = None
#        self.DialMode = "manual"
        self.DialMode = None
        self.SlaveDevice = None
        self.EthDevice = None    
        self.ServiceName = None    
        self.AcName = None    
        self.SyncPPP = None    
        self.InitString = None
        self.Secure = None
        self.PhoneInNumber = None
        self.Callback = Callback()
        self.Compression = Compression()

    def createCallback(self):
        if not self.Callback:
            self.Callback = Callback()
        return self.Callback
    
    def createCompression(self):
        if not self.Compression:
            self.Compression = Compression()            
        return self.Compression
    
    def createPPPOptions(self):
        if not self.PPPOptions:
            self.PPPOptions = PPPOptions()
        return self.PPPOptions

DM_AUTO = 'auto'
DM_MANUAL = 'manual'

DialModes = { DM_AUTO : _('auto'),
              DM_MANUAL : _('manual') }

__country_code = {
    _("None") : 0,
    _("Afghanistan") : 93,
    _("Albania") : 355,
    _("Algeria") : 213,
    _("American Samoa") : 684,
    _("Andorra") : 376,
    _("Argentina") : 54,
    _("Australia") : 61,
    _("Austria") : 43,
    _("Belarus") : 375,
    _("Belgium") : 32,
    _("Bosnia and Hercegovina") : 387,
    _("Brazil") : 55,
    _("British Virgin Islands") : 1,
    _("Bulgaria") : 359,
    _("Canada") : 1,
    _("Central African Republic") : 236,
    _("Chile") : 56,
    _("China") : 86,
    _("Colombia") : 47,
    _("Croatia") : 385,
    _("Cuba") : 53,
    _("Cyprus") : 357,
    _("Czech Republic") : 420,
    _("Denmark") : 45,
    _("Finland") : 358,
    _("France") : 33,
    _("Germany") : 49,
    _("Greece") : 30,
    _("Hong Kong") : 852,
    _("Hungary") : 36,
    _("Iceland") : 354,
    _("India") : 91,
    _("Indonesia") : 62,
    _("Ireland") : 353,
    _("Israel") : 972,
    _("Italy") : 39,
    _("Japan") : 81,
    _("Kazakhstan") : 7,
    _("Korea North") : 850,
    _("Korea Republic") : 82,
    _("Liechtenstein") : 423,
    _("Lithuania") : 370,
    _("Luxembourg") : 352,
    _("Macedonia") : 389,
    _("Malaysia") : 60,
    _("Malta") : 356,
    _("Mexico") : 52,
    _("Moldova") : 373,
    _("Monaco") : 377,
    _("Netherlands") : 31,
    _("New Zealand") : 64,
    _("Norway") : 47,
    _("Palestine") : 970,
    _("Philippines") : 63,
    _("Poland") : 48,
    _("Portugal") : 351,
    _("Romania") : 30,
    _("Russia") : 7,
    _("Singapore") : 65,
    _("Slovakia") : 421,
    _("Slovenia") : 386,
    _("Spain") : 34,
    _("Sweden") : 46,
    _("Switzerland") : 41,
    _("Taiwan") : 886,
    _("Thailand") : 66,
    _("Turkey") : 90,
    _("Ukraine") : 380,
    _("United Kingdom") : 44,
    _("United States of America") : 1,
    _("Vietnam") : 84,
    _("Serbia") : 381, # FIXED: [175078] String (country name) change request
    _("Montenegro") : 381
    }


# pylint: disable-msg=W0201

class Dialup(Dialup_base):
    "Class for all Dialup Interfaces"
    intkeydict = {
                    'Mru' : 'MRU', 
#                    'Mtu' : 'MRU', 
                 }

    def load(self, parentConf, parent):
        "Load the Configuration from the parentConf"
        #print >> sys.stderr, "LOAD Dialup"

        conf = parentConf
        devidstr = parent.DeviceId
        for selfkey in self.intkeydict.keys():
            confkey = self.intkeydict[selfkey]
            if conf.has_key(confkey) and len(conf[confkey]):
                setattr(self, selfkey, int(conf[confkey]))


        if parentConf.has_key('DEMAND'):
            if parentConf['DEMAND'] == 'yes':
                self.DialMode = DM_AUTO
            else:
                self.DialMode = DM_MANUAL

        if self.Login:
            if not hasattr(self, "Password") or self.Password == None:
                self.Password = ""
            log.log(6, "Looking for %s" % self.Login)
            papconf = getPAPConf()
            chapconf = getCHAPConf()
            for conf in [chapconf, papconf]:
                if conf.has_key(self.Login):
                    log.log(6, "Found %s" % conf[self.Login])
                    if conf[self.Login].has_key("*"):
                        self.Password = conf[self.Login]["*"]
                    if conf[self.Login].has_key(devidstr):
                        self.Password = conf[self.Login][devidstr]
                        log.log(6, "Found %s" % self.Password)
                        break
        else:
            log.log(6, "No self.login!!!")

    def save(self, parentConf,        # pylint: disable-msg=W0613
             deviceid, olddeviceid):
        "Save the Configuration to parentConf"
        log.log(6, "Dialup.save")
        conf = parentConf
        for selfkey in self.intkeydict.keys():
            confkey = self.intkeydict[selfkey]
            if hasattr(self, selfkey) and getattr(self, selfkey):
                conf[confkey] = str(getattr(self, selfkey))
            else: del conf[confkey]

        if self.Login != None:
            papconf = getPAPConf()
            chapconf = getCHAPConf()
            # set *
            papconf[self.Login] = str(self.Password)
            chapconf[self.Login] = str(self.Password)
            # set specific auth also
            papconf[[self.Login, 
                     deviceid]] = str(self.Password)
            chapconf[[self.Login, 
                      deviceid]] = str(self.Password)
        if self.DialMode == DM_AUTO:
            parentConf['DEMAND'] = 'yes'
        else:
            parentConf['DEMAND'] = 'no'
        log.log(6, "Dialup.end")


# FIXME: [131556] system-config-network lacks support for pppoatm
class DslDialup(Dialup):
    "Class for all DSL Dialup Interfaces"
    boolkeydict = { 'SyncPPP' : 'SYNCHRONOUS',
                    'Persist' : 'PERSIST',
                    'DefRoute' : 'DEFROUTE',
                    }

    keydict = { 'ProviderName' : 'PROVIDER',
                'Login' : 'USER',
                'EthDevice' : 'ETH',
                'SlaveDevice' : 'SLAVE_DEVICE',
                'ServiceName' : 'SERVICENAME',
                'AcName' : 'ACNAME',
                }

    def load(self, parentConf, parent):
        "Load the Configuration from the parentConf"
        conf = parentConf

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if conf.has_key(confkey):
                setattr(self, selfkey, conf[confkey])
                #print "self." + selfkey + " = " + conf[confkey]

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if conf.has_key(confkey):
                if conf[confkey] == 'yes':
                    setattr(self, selfkey, True)
                else:
                    setattr(self, selfkey, False)
            else:
                setattr(self, selfkey, False)

        # We need self.login, so we call it this late
        Dialup.load(self, parentConf, parent)

        if conf.has_key("PASS"):
            self.Password = conf["PASS"]

        if parentConf.has_key('IDLETIMEOUT'):
            self.HangupTimeout = int(parentConf['IDLETIMEOUT'])

    def save(self, parentConf, devidstr, olddeviceid):
        "Save the Configuration to parentConf"
        Dialup.save(self, parentConf, devidstr, olddeviceid)

        conf = parentConf

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if hasattr(self, selfkey) and getattr(self, selfkey):
                conf[confkey] = getattr(self, selfkey)
            else: conf[confkey] = ""

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if hasattr(self, selfkey) and getattr(self, selfkey):
                conf[confkey] = 'yes'
            else:
                conf[confkey] = 'no'
        
        # The ACNAME is used for the server name
        if self.Login and self.AcName:
            papconf = getPAPConf()
            chapconf = getCHAPConf()
            papconf[[self.Login, self.AcName]] = str(self.Password)
            chapconf[[self.Login, self.AcName]] = str(self.Password)

        if self.HangupTimeout:
            parentConf['IDLETIMEOUT'] = str(self.HangupTimeout)

        if not conf.has_key('CONNECT_TIMEOUT'):
            conf['CONNECT_TIMEOUT'] = '60'

        if not conf.has_key('CONNECT_POLL'):
            conf['CONNECT_POLL'] = '6'

        if not conf.has_key('CLAMPMSS'):
            conf['CLAMPMSS'] = '1412'

        if not conf.has_key('LCP_INTERVAL'):
            conf['LCP_INTERVAL'] = '20'

        if not conf.has_key('LCP_FAILURE'):
            conf['LCP_FAILURE'] = '3'

        if not conf.has_key('PPPOE_TIMEOUT'):
            conf['PPPOE_TIMEOUT'] = '80'

        if not conf.has_key('PING'):
            conf['PING'] = '.'

        if not conf.has_key('FIREWALL'):
            conf['FIREWALL'] = 'NONE'

        if not conf.has_key('PIDFILE'):
            conf['PIDFILE'] = '/var/run/pppoe-adsl.pid'

        for i in conf.keys():
            if not conf[i]: 
                del conf[i]

        if conf.has_key('PASS'):
            del conf['PASS']

        if not conf.has_key('PEERDNS'):
            conf['PEERDNS'] = "no"

        conf.write()


class IsdnDialup(Dialup):
    "Class for all ISDN Dialup Interfaces"
    boolkeydict = { 'Secure' : 'SECURE',
                    'ChannelBundling' : 'BUNDLING',
                    'Persist' : 'PERSIST',
                    }

    intkeydict = {'DialMax' : 'DIALMAX',
                  'HangupTimeout' : 'HUPTIMEOUT',
                  }

    keydict = { 'MSN' : 'MSN',
                'ProviderName' : 'PROVIDER',
                'Login' : 'USER',
                'Password' : 'PASSWORD',
                'EncapMode' : 'ENCAP',
                'DialMode' : 'DIALMODE',
                'Prefix' : 'PREFIX',
                'Areacode' : 'AREACODE',
                'Regioncode' : 'REGIONCODE',
                'PhoneNumber' : 'PHONE_OUT',
                'PhoneInNumber': 'PHONE_IN',
                'PrimaryDNS' : 'DNS1',
                'SecondaryDNS' : 'DNS2',
                'ChargeHup' : 'CHARGEHUP',
                'ChargeInt' : 'CHARGEINT',
                'Authentication' : 'AUTH',
                'Ihup' : 'IHUP',
                'SlaveDevice' : 'SLAVE_DEVICE',
                'Layer2' : 'L2_PROT',
                'Layer3' : 'L3_PROT',
                }

    def load(self, parentConf, parent):
        "Load the Configuration from the parentConf"
        conf = parentConf

        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if conf.has_key(confkey):
                setattr(self, selfkey, conf[confkey])
                #print "self." + selfkey + " = " + conf[confkey]

        for selfkey in self.intkeydict.keys():
            confkey = self.intkeydict[selfkey]
            if conf.has_key(confkey) and len(conf[confkey]):
                setattr(self, selfkey, int(conf[confkey]))
                #setattr(self, selfkey, int(conf[confkey]))
                #print "self." + selfkey + " = " + conf[confkey]

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if conf.has_key(confkey):
                if conf[confkey] == 'on':
                    setattr(self, selfkey, True)
                    #setattr(self, selfkey, True)
                else:
                    setattr(self, selfkey, False)
                    #setattr(self, selfkey, False)
            else:
                setattr(self, selfkey, False)
                #setattr(self, selfkey, False)

        # We need self.login, so we call it this late
        Dialup.load(self, parentConf, parent)

        if conf.has_key('DEFROUTE'):
            if conf['DEFROUTE'] == 'yes':
                self.DefRoute = True
            else:
                self.DefRoute = False

        if not conf.has_key('PPPOPTIONS'):
            del self.PPPOptions 

            options = conf['PPPOPTIONS']
            for o in options.split():
                opt = PPPOption(o)                
                self.PPPOptions.append(opt)

        if parent:
            if conf.has_key('LOCAL_IP'):
                parent.IP = conf['LOCAL_IP']
            if conf.has_key('REMOTE_IP'):
                parent.Gateway = conf['REMOTE_IP']
            if conf.has_key('BOOT'):
                if conf['BOOT'] == 'on':
                    parent.OnBoot = True
                else:
                    parent.OnBoot = False

        self.Compression.load(conf) 

        if conf.has_key('CALLBACK'):
            if conf['CALLBACK'] == 'in' or conf['CALLBACK'] == 'out':
                self.Callback.load(conf)
            else:
                del self.Callback 

        if conf.has_key("PASSWORD"):
            self.Password = conf["PASSWORD"]

        self.commit()
        self.setunmodified()

    def save(self, parentConf, devidstr, olddeviceid):
        "Save the Configuration to parentConf"
        log.log(6, "IsdnDialup.save")
        Dialup.save(self, parentConf, devidstr, olddeviceid)
        conf = parentConf
        
        for selfkey in self.keydict.keys():
            confkey = self.keydict[selfkey]
            if hasattr(self, selfkey) and getattr(self, selfkey) != None:
                conf[confkey] = getattr(self, selfkey)
            else: conf[confkey] = ""

        for selfkey in self.intkeydict.keys():
            confkey = self.intkeydict[selfkey]
            if hasattr(self, selfkey) and getattr(self, selfkey) != None:
                conf[confkey] = str(getattr(self, selfkey))
            else: conf[confkey] = ""

        for selfkey in self.boolkeydict.keys():
            confkey = self.boolkeydict[selfkey]
            if hasattr(self, selfkey) and getattr(self, selfkey) == True:
                conf[confkey] = 'on'
            else:
                conf[confkey] = 'off'

        if self.DefRoute:
            conf['DEFROUTE'] = 'yes'
        else:
            conf['DEFROUTE'] = 'no'

        if conf.has_key('PEERDNS') and conf['PEERDNS'] == "yes":
            if conf['DNS1']: 
                del conf['DNS1']
            if conf['DNS2']: 
                del conf['DNS2']

        if self.PPPOptions:
            opt = ""
            for val in self.PPPOptions:
                if opt != "": 
                    opt = opt + ' '
                opt = opt + val
            conf['PPPOPTIONS'] = opt
        else:
            del conf['PPPOPTIONS']

        #parent = self.getParent()

        if conf.has_key('LOCAL_IP'):
            del conf['LOCAL_IP']
        if conf.has_key('REMOTE_IP'):
            del conf['REMOTE_IP']
        if conf.has_key('BOOT'):
            del conf['BOOT']

        if conf.has_key('PASSWORD'):
            del conf['PASSWORD']

        if self.Compression:
            self.Compression.save(conf)

        log.log(6, "Callback.save")

        if self.Callback: 
            conf['CALLBACK'] = self.Callback.Type
            self.Callback.save(conf)
        else:
            conf['CALLBACK'] = 'off'
            
        if conf['CALLBACK'] == 'off':
            for key in ['CBHUP', 'CBDELAY', 'CBCP', 'CBCP_MSN']:
                if conf.has_key(key):
                    del conf[key]

        for i in conf.keys():
            if not conf[i]: 
                del conf[i]

        if not conf.has_key('PEERDNS'):
            conf['PEERDNS'] = "no"

        conf.write()
        log.log(6, "IsdnDialup.save end")

class ModemDialup(Dialup):
    "Class for all Modem Dialup Interfaces"

    boolwvdict = { 'StupidMode' : 'Stupid Mode',
                   }

    wvdict = { 'Login' : 'Username',
               'Password' : 'Password',
               'Prefix' : 'Dial Prefix',
               'Areacode' : 'Area Code',
               'PhoneNumber' : 'Phone',
               }

    def load(self, parentConf, parent):
        "Load the Configuration from the parentConf"
        # FIXME: [177931] Stupid Mode goes away in /etc/wvdial.conf 
        # when a dialup connection is saved
        # FIXME: [168087] Fails to retain ppp connection passwords 
        # containing spaces between saves
        name = parent.DeviceId
        if parentConf.has_key('WVDIALSECT'):
            name = parentConf['WVDIALSECT']

        conf = ConfSMB.ConfSMB(filename = getRoot() + WVDIALCONF)

        sectname = 'Dialer ' + name

        for selfkey in self.wvdict.keys():
            confkey = self.wvdict[selfkey]
            value = None
            if conf.has_key(sectname) and conf[sectname].has_key(confkey):
                value = conf[sectname][confkey]
            elif conf.has_key('Dialer Defaults') \
               and conf['Dialer Defaults'].has_key(confkey):
                value = conf['Dialer Defaults'][confkey]

            if value:
                setattr(self, selfkey, value)


        for selfkey in self.boolwvdict.keys():
            confkey = self.boolwvdict[selfkey]
            value = None
            if conf.has_key(sectname) and conf[sectname].has_key(confkey):
                value = conf[sectname][confkey]
            elif conf.has_key('Dialer Defaults') \
               and conf['Dialer Defaults'].has_key(confkey):
                value = conf['Dialer Defaults'][confkey]

            if value and value != '0':
                setattr(self, selfkey, True)
            else:
                setattr(self, selfkey, False)

        # We need self.login, so we call it this late
        Dialup.load(self, parentConf, parent)

        #
        # Read Modem Init strings
        #
        if conf.has_key(sectname) and conf[sectname].has_key('Init3'):
            self.InitString = conf[sectname]['Init3']

        if self.Compression:
            self.Compression.load(parentConf)

        if parentConf.has_key('PROVIDER'):
            self.ProviderName = parentConf['PROVIDER']

        if parentConf.has_key('PERSIST'):
            self.Persist = parentConf['PERSIST'] == 'yes'

        if parentConf.has_key('DEFROUTE'):
            self.DefRoute = parentConf['DEFROUTE'] == 'yes'

        if parentConf.has_key('IDLETIMEOUT'):
            self.HangupTimeout = int(parentConf['IDLETIMEOUT'])

        if parentConf.has_key('PPPOPTIONS'):
            options = parentConf['PPPOPTIONS']
            for o in options.split():
                opt = PPPOption(o)
                self.PPPOptions.append(opt)
        else:
            del self.PPPOptions
        #
        # Workaround for backporting rp3-config stuff
        #
        if parentConf.has_key('MODEMNAME'):
            self.Inherits = parentConf['MODEMNAME']
        elif conf[sectname].has_key('Inherits') and \
             conf[sectname]['Inherits'] == 'Dialer Defaults':
            if conf.has_key('Dialer Defaults') and \
               conf['Dialer Defaults'].has_key('Modem') and \
               conf['Dialer Defaults'].has_key('Baud'):
                modemdev = conf['Dialer Defaults']['Modem']
                modembaud = conf['Dialer Defaults']['Baud']
                for sect in conf.keys():
                    if (len(sect) <= 5) or (sect[:5] != 'Modem'):
                        #print "Skipping " + sect
                        continue
                    if conf[sect].has_key('Modem') and \
                       conf[sect].has_key('Baud') and \
                       conf[sect]['Modem'] == modemdev and \
                       conf[sect]['Baud'] == modembaud:
                        #print "Found " + sect
                        self.Inherits = sect
                        break


    def save(self, parentConf, deviceid, olddeviceid):
        "Save the Configuration to parentConf"
        Dialup.save(self, parentConf, deviceid, olddeviceid)
        if self.Inherits:
            devname = self.Inherits
            parentConf['MODEMNAME'] = devname
            name = deviceid
        else:
            devname = '*'
            name = "Default"

        # set WVDIALSECT in ifcfg-ppp[0-9] to DeviceId
        parentConf['WVDIALSECT'] = name
        sectname = 'Dialer ' + name
        self.write_wvdial(devname, sectname)

        # Correct PAPNAME in ifcfg-ppp[0-9]
        if self.Login:
            parentConf['PAPNAME'] = self.Login
        
        if self.PPPOptions:
            opt = ""
            for val in self.PPPOptions:
                if opt != "": 
                    opt = opt + ' '
                opt = opt + val
            parentConf['PPPOPTIONS'] = opt
        else:
            # CHECK - deleting PPP option #128058
            parentConf['PPPOPTIONS'] = None


        if self.Persist:
            parentConf['PERSIST'] = 'yes'
        else:
            parentConf['PERSIST'] = 'no'

        if self.DefRoute:
            parentConf['DEFROUTE'] = 'yes'
        else:
            parentConf['DEFROUTE'] = 'no'

        if self.ProviderName:
            parentConf['PROVIDER'] = self.ProviderName

        if self.HangupTimeout:
            parentConf['IDLETIMEOUT'] = str(self.HangupTimeout)

        if self.Inherits:
            hwlist = NCHardwareList.getHardwareList()
            for hw in hwlist:
                if hw.Name == self.Inherits:
                    if hw.Modem:
                        parentConf['MODEMPORT'] = str(hw.Modem.DeviceName)
                        parentConf['LINESPEED'] = str(hw.Modem.BaudRate)
                        break

        if not parentConf.has_key('PEERDNS'):
            parentConf['PEERDNS'] = "no"

        if self.Compression:
            self.Compression.save(parentConf)

        self.write_peers(deviceid, olddeviceid, name)

    def write_wvdial(self, devname, sectname):        
        "Write the wvdial section"
        conf = ConfSMB.ConfSMB(filename=getRoot() + WVDIALCONF)
        conf.chmod(0600)
        if not conf.has_key(sectname):
            conf[sectname] = ConfSMB.ConfSMBSubDict(conf, sectname)
        
        for selfkey in self.wvdict.keys():
            confkey = self.wvdict[selfkey]
            if hasattr(self, selfkey) and getattr(self, selfkey) != None:
                conf[sectname][confkey] = str(getattr(self, selfkey))
            elif conf[sectname].has_key(confkey):
                del conf[sectname][confkey]
        for selfkey in self.boolwvdict.keys():
            confkey = self.boolwvdict[selfkey]
            if hasattr(self, selfkey) and getattr(self, selfkey):
                conf[sectname][confkey] = '1'
            # FIXME: [177931] Stupid Mode goes away in /etc/wvdial.conf
            # when a dialup connection is saved
            else:
                conf[sectname][confkey] = '0'
                #
                # Write Modem Init strings
                #
        if conf[sectname].has_key('Init'):
            del conf[sectname]['Init']
        if not conf[sectname].has_key('Init1'):
            conf[sectname]['Init1'] = 'ATZ'
        #
        # Better not be smarter than the user
        #
        #if not conf[sectname].has_key('Init2'):
        #    conf[sectname]['Init2'] = 'ATQ0 V1 E1 S0=0 &C1 &D2'
        if self.InitString:
            conf[sectname]['Init3'] = str(self.InitString)
        #else: del conf[sectname]['Init3']
        conf[sectname]['Inherits'] = devname
        for i in conf.keys():
            if not conf[i]:
                del conf[i]
        conf.write()

    def write_peers(self, deviceid, olddeviceid, name):
        
        # Write /etc/ppp/peers/DeviceId
        
        # bug #77763
        peerdir = getRoot() + PPPDIR + "/peers/"
        if not os.path.isdir(peerdir):
            mkdir(peerdir)
        
        if olddeviceid and (olddeviceid != deviceid):
            unlink(peerdir + olddeviceid)
        
        filename = peerdir + deviceid
        try:
            mfile = open(filename, "w")
            line = str('connect "/usr/bin/wvdial --remotename '
                       '%s --chat \'%s\'"' % (deviceid, name))
            mfile.write(line + '\n')
            log.lch(2, filename, line)
            mfile.close()
        except KeyError:
            pass


__author__ = "Harald Hoyer <harald@redhat.com>"
