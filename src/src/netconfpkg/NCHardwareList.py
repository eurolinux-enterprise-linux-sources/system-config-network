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
import glob
import os
from netconfpkg import NCisdnhardware
from netconfpkg.NCHardware import HW_CONF, HW_SYSTEM, HW_OK, Card, Hardware
from netconfpkg.NC_functions import (_, getRoot, HWCONF, NETCONFDIR, WVDIALCONF,
                                     log, ISDN, MODEM, CRTSCTS, ETHERNET, QETH,
                                     getDeviceType, TOKENRING, WIRELESS, 
                                     MODULESCONF, getTestEnv)
from netconfpkg.conf.Conf import (Conf, FileMissing,
                                  VersionMismatch)
from netconfpkg.conf.ConfModules import ConfModInfo, ConfModules
from netconfpkg.conf.ConfSMB import ConfSMB
from netconfpkg.gdt import Gdtlist, gdtlist_properties
import ethtool
from netconfpkg.executil import execWithCapture


ModInfo = None
__isdnmodulelist = []
try:
    __msg =  execWithCapture("/bin/sh", [ "/bin/sh", "-c", 
    "find /lib/modules/$(uname -r)/*/drivers/isdn" +
    " -name '*.?o' -printf '%f ' 2>/dev/null" ])
    __isdnmodulelist = __msg.split()
except:
    pass

__wirelessmodulelist = []
try:
    __msg =  execWithCapture("/bin/sh", [ "/bin/sh", "-c", 
    "find /lib/modules/$(uname -r)/*/drivers/net/wireless" +
    " -name '*.?o' -printf '%f ' 2>/dev/null" ])
    __wirelessmodulelist = __msg.split()
except:
    pass


#__networkmodulelist = []
#try:
#    __msg =  execWithCapture("/bin/sh", 
#                             [ "/bin/sh", "-c", 
#                               "find /lib/modules/$(uname -r)/*/drivers/net" +
#                               " -name '*.?o' -printf '%f ' 2>/dev/null" ])
#    __networkmodulelist.append(__isdnmodulelist)
#    __networkmodulelist = string.split(__msg)
#except:
#    pass


def getModInfo():
    # pylint: disable-msg=W0603
    global ModInfo
    
    if getTestEnv():
        return None
    
    if ModInfo == None:
#         ModInfo = {}
#         for mod in __networkmodulelist:
#             if mod.find(".ko") != -1:
#                 i = mod.find(".ko")
#                 mod = mod[:i]

#             try:
#                 desc = execWithCapture("/sbin/modinfo", 
#                                        [ "/sbin/modinfo", "-F", 
#                                          "description", mod ])
#                 ModInfo[mod] = {}
#                 ModInfo[mod]['type'] = 'eth'
#                 ModInfo[mod]['description'] = desc.strip()
#             except:
#                 pass
            
        for path in [ '/boot/module-info',
                      NETCONFDIR + '/module-info',
                      './module-info' ]:
            try:
                ModInfo = ConfModInfo(filename = path)
            except (VersionMismatch, FileMissing):
                continue
            break

    return ModInfo

class MyConfModules(ConfModules):
    def __init__(self, filename = None):
        # if we put getRoot() in the default parameter it will
        # have the value at parsing time
        if filename == None:
            filename = getRoot() + MODULESCONF
        # FIXME: [187640] Support aliases in /etc/modprobe.d/
        ConfModules.__init__(self, filename)

    def __delitem__(self, varname):
        # delete *every* instance...
        place = self.tell()
        for key in self.vars[varname].keys():
            self.rewind()

            # workaround for broken regexp implementation
            restr = '^[\\t ]*' + key + '[\\t ]+' + varname
            while self.findnextline(restr):
                #print "1) Deleting %s" % self.line
                self.deleteline()

            restr = '^[\\t ]*' + key + '[\\t ]+\\-k[\\t ]+' + varname
            while self.findnextline(restr):
                #print "2) Deleting %s" % self.line
                self.deleteline()

        del self.vars[varname]
        log.ldel(2, self.filename, varname)
        self.seek(place)


    def splitopt(self, opt):
        eq = opt.find('=')
        if eq > 0:
            return (opt[:eq], opt[eq+1:])
        else:
            return (opt, None)

    def joinoptlist(self, mdict):
        optstring = ''
        for key in mdict.keys():
            if mdict[key] != None:
                optstring = optstring + key + '=' + mdict[key] + ' '
            else:
                optstring = optstring + key + ' '

        return optstring



_MyConfModules = None
_MyConfModules_root = getRoot()

def getMyConfModules(refresh = None):
    # pylint: disable-msg=W0603
    global _MyConfModules
    global _MyConfModules_root

    if _MyConfModules == None or refresh or \
           _MyConfModules_root != getRoot() :
        _MyConfModules = MyConfModules()
        _MyConfModules_root = getRoot()
    return _MyConfModules

_MyWvDial = None
_MyWvDial_root = getRoot()

def getMyWvDial(create_if_missing = None):
    # pylint: disable-msg=W0603
    global _MyWvDial
    global _MyWvDial_root

    if _MyWvDial == None or _MyWvDial_root != getRoot():
        _MyWvDial = ConfSMB(getRoot() + WVDIALCONF,
                           create_if_missing = create_if_missing)
        _MyWvDial_root = getRoot()

    return _MyWvDial

class ConfHWConf(Conf):
    "Special Hardware Conf Class"
    def __init__(self):
        Conf.__init__(self, getRoot() + HWCONF)
        self.vars = {}

    def read(self):
        Conf.read(self)
        self.initvars()

    def initvars(self):
        self.vars = {}

        if not os.access(getRoot() + HWCONF, os.R_OK):
            return

        fp = open(getRoot() + HWCONF, 'r')
        hwlist = fp.read()
        hwlist = hwlist.split("-\n")
        pos = 0
        for hw in hwlist:
            if not len(hw):
                continue
            items = hw.split('\n')
            hwdict = {}
            for item in items:
                if not len(item):
                    continue
                vals = item.split(":")
                if len(vals) <= 1:
                    # skip over bad/malformed lines
                    continue
                # Some of the first words are used as dict keys server side
                # so this just helps make that easier
                strippedstring = vals[1].strip()
                vals[1] = strippedstring
                hwdict[vals[0]] = " ".join(vals[1:])
            self.vars[pos] = hwdict
            pos = pos + 1

    def __getitem__(self, varname):
        if self.vars.has_key(varname):
            return self.vars[varname]
        else:
            return None

    def keys(self):
        return self.vars.keys()

class HardwareList_base(Gdtlist):
    gdtlist_properties(Hardware)

class HardwareList(HardwareList_base):
    s390devs = { 
                 "lcs" : "lcs" ,
                 "osad" : "",
                 "eth" : "qeth",
                 "hsi" : "qeth",
                 "tr" : "qeth",
                 }

    def __init__(self):
        HardwareList_base.__init__(self)
        # FIXME: [198070] use modinfo to determine options
        self.keydict = { }

    def addHardware(self, mtype = None):
        from netconfpkg.NCHardwareFactory import getHardwareFactory
#        i = HardwareList_base.addHardware(self)
        
        hwf = getHardwareFactory()
        hwc = hwf.getHardwareClass(mtype)
        if hwc:
            newhw = hwc()
            self.append(newhw)
#        else: # FIXME: !!
#            raise TypeError
        return len(self)-1

    def updateFromSys(self, hdellist):
        modules = getMyConfModules()
        modinfo = getModInfo()            
        #
        # Read in actual system state
        #
        for syspath in glob.glob(getRoot() + '/sys/class/net/*'):
            device = os.path.basename(syspath)
            mod = None
            try:                
                mpath = '%s/device/driver' % syspath
                log.log(5, "Checking %s" % mpath)
                mod = os.path.basename(os.readlink(mpath))
            except:                
                pass

            try:
                fp = open("%s/type" % syspath)
                line = fp.readlines()
                fp.close()
                line = " ".join(line)
                line.strip()
                log.log(5, "type %s = %s" % (device, line))
                mtype = int(line)
                if mtype >= 256:
                    continue
            except:
                pass

            log.log(5, "%s = %s" % (device, mod))
            
            h = None
            for h in self:
                if h.Name == device:
                    break
            # pylint: disable-msg=W0631
            if h and h.Name == device and h.Status != HW_SYSTEM:
                continue

#            if device[:3] != "eth":
#                continue

            # No Alias devices
            if device.find(':') != -1:
                continue

            if mod != None and mod != "":
                # if it is already in our HW list do not delete it.
                for h in hdellist:
                    if h.Name == device and h.Card.ModuleName == mod:
                        log.log(5, "Found %s:%s, which is already in our list!"
                                % (device, mod))
                        hdellist.remove(h)
                        break
                    else:
                        log.log(5, "%s != %s and %s != %s" 
                                % (h.Name, device, 
                                   h.Card.ModuleName, mod))
                else:
                    for h in self:
                        if h.Name == device and h.Card.ModuleName == mod:
                            break
                    else:
                        hwtype = getDeviceType(device, module = mod)
                        i = self.addHardware(hwtype)
                        hw = self[i]
                        hw.Name = device
                        hw.Description = mod
                        hw.Status = HW_SYSTEM
                        hw.Type = hwtype
                        hw.Card = Card()
                        hw.Card.ModuleName = mod
                        if modinfo:
                            for info in modinfo.keys():
                                if info == mod:
                                    if modinfo[info].has_key('description'):
                                        hw.Description = \
                                            modinfo[info]['description']

                        for selfkey, confkey in self.keydict.items():
                            if (modules[hw.Card.ModuleName] and
                                    modules[hw.Card.ModuleName]
                                    ['options'].has_key(confkey)):
                                setattr(hw.Card, selfkey, 
                                        modules[hw.Card.ModuleName]
                                        ['options'][confkey])
                        hw.setunmodified()

        return hdellist


    def updateFromHal(self, hdellist):
        from netconfpkg import NCBackendHal
        hal = NCBackendHal.NCBackendHal()
        cards = hal.probeCards()
        for hw in cards:
            # if it is already in our HW list do not delete it.
            for h in hdellist:
                if (h.Name == hw.Name 
                    and h.Card.ModuleName == hw.Card.ModuleName):
                    log.log(5, 
                    "Found %s:%s, which is already in our list!" 
                    % (hw.Name, hw.Card.ModuleName))
                    hdellist.remove(h)
                    break
                else:
                    log.log(5, "%s != %s and %s != %s" 
                            % (h.Name, hw.Name, 
                               h.Card.ModuleName, 
                               hw.Card.ModuleName))
            else: 
                for h in self:
                    if(h.Name == hw.Name 
                       and h.Card.ModuleName == hw.Card.ModuleName):
                        break
                    else:
                        log.log(5, "%s != %s and %s != %s" 
                                % (h.Name, hw.Name, 
                                   h.Card.ModuleName, 
                                   hw.Card.ModuleName))
                else:
                    hw.Status = HW_SYSTEM
                    self.append(hw) 
                    hw.setunmodified()        

        return hdellist

    def updateFromSystem(self):
        log.log(5, "updateFromSystem")
        
        hdellist = []

        for h in self:
            if h.Status == HW_SYSTEM:
                hdellist.append(h)

        log.log(5, "updateFromHal")
        try:
            hdellist = self.updateFromHal(hdellist)
        except:
            pass
        log.log(5, str(self))

        log.log(5, "updateFromSys")
        try:
            hdellist = self.updateFromSys(hdellist)
        except:
            pass
        log.log(5, str(self))

        for h in hdellist:
            log.log(5, "Removing %s from HWList" % h.Name)
            self.remove(h) 

        del hdellist

        log.log(5, str(self))

    def updateFromModules(self):
        modules = getMyConfModules()
        modinfo = getModInfo()
        #
        # Read /etc/modprobe.d/network.conf
        #
        for mod in modules.keys():
            if modules[mod].has_key('alias'):
                module = modules[mod]['alias']
            else: module = None

            mtype = getDeviceType(mod, module)

            if mtype == _('Unknown'):
                continue

            h = None
            for h in self:
                if h.Name == mod:
                    break
            # pylint: disable-msg=W0631
            if h and h.Name == mod:
                continue

            i = self.addHardware(mtype)
            hw = self[i]
            hw.Name = mod
            hw.Description = module
            hw.Type = mtype
            hw.Card = Card()
            hw.Card.ModuleName = module
            hw.Status = HW_CONF
            if module and modinfo:
                for info in modinfo.keys():
                    if info == module:
                        if modinfo[info].has_key('description'):
                            hw.Description = modinfo[info]['description']

            for selfkey in self.keydict.keys():
                confkey = self.keydict[selfkey]
                if modules[hw.Card.ModuleName] and \
                       modules[hw.Card.ModuleName]['options'].has_key(confkey):
                    setattr(hw.Card, selfkey, 
                            modules[hw.Card.ModuleName]['options'][confkey])

    def tostr(self, prefix_string = None):
        "returns a string in gdt representation"
        #print "tostr %s " % prefix_string
        if prefix_string == None:
            prefix_string = self.__class__.__name__
        mstr = ""
        for value in self:
            if isinstance(value, Hardware):
                mstr += value.tostr("%s.%s.%s" 
                                    % (prefix_string, value.Type, 
                                       value.Name))
        return mstr

    def fromstr(self, vals, value):
        if len(vals) <= 1:
            return
        if vals[0] == "HardwareList":
            del vals[0]
        else:
            return
        for dev in self:
            if dev.Name == vals[1]:
                if dev.Type != vals[0]:
                    self.remove(dev) 
                    log.log(1, "Deleting device %s" % vals[1] )
                    break
                dev.fromstr(vals[2:], value) # pylint: disable-msg=W0212
                return
        log.log(4, "Type = %s, Name = %s" % (vals[0], vals[1]))
        i = self.addHardware(vals[0])
        dev = self[i]
        dev.Name = vals[1]
        dev.fromstr(vals[2:], value)  # pylint: disable-msg=W0212


    def load(self):
        #hwconf = ConfHWConf()

        # first clear the list
        self.__delslice__(0, len(self)) 

        # FIXME: move HW detection to NCDev*
        dosysupdate = True
        if getTestEnv():
            dosysupdate = False
        if dosysupdate:
            self.updateFromSystem()

        self.updateFromModules()

        for hw in self:
            if hw.Name == "ISDN Card 0":
                break
        else:
            #
            # XXX FIXME... this is not OO
            #
            isdncard = NCisdnhardware.ConfISDN()
            if isdncard.load() > 0:
                i = self.addHardware(ISDN)
                hw = self[i]
                hw.Name = "ISDN Card 0"
                hw.Description = isdncard.Description
                hw.Type = ISDN
                hw.Status = HW_CONF
                hw.Card = Card()
                hw.Card.ModuleName = isdncard.ModuleName
                hw.Card.Type = isdncard.Type
                hw.Card.IoPort = isdncard.IoPort
                hw.Card.IoPort1 = isdncard.IoPort1
                hw.Card.IoPort2 = isdncard.IoPort2
                hw.Card.Mem = isdncard.Mem
                hw.Card.IRQ = isdncard.IRQ
                hw.Card.ChannelProtocol = isdncard.ChannelProtocol
                hw.Card.Firmware = isdncard.Firmware
                hw.Card.DriverId = isdncard.DriverId
                hw.Card.VendorId = isdncard.VendorId
                hw.Card.DeviceId = isdncard.DeviceId

        #
        # FIXME: This is not OO!
        #
        try:
            wvdial = ConfSMB(getRoot() + WVDIALCONF)
        except FileMissing:
            pass
        else:
            for dev in wvdial.keys():
                if dev[:5] != 'Modem':
                    continue

                i = self.addHardware(MODEM)
                hw = self[i]
                hw.Name = dev
                hw.Description = 'Generic Modem'
                hw.Type = MODEM
                hw.Status = HW_CONF
                hw.createModem()
                if not wvdial[dev].has_key('Modem'):
                    wvdial[dev]['Modem'] = '/dev/modem'
                hw.Modem.DeviceName = wvdial[dev]['Modem']

                if not wvdial[dev].has_key('Baud'):
                    wvdial[dev]['Baud'] = '38400'
                try:
                    hw.Modem.BaudRate = int(wvdial[dev]['Baud'])
                except ValueError:
                    hw.Modem.BaudRate = 38400

                if not wvdial[dev].has_key('SetVolume'):
                    wvdial[dev]['SetVolume'] = '0'
                hw.Modem.ModemVolume = int(wvdial[dev]['SetVolume'])

                if not wvdial[dev].has_key('Dial Command'):
                    wvdial[dev]['Dial Command'] = 'ATDT'
                hw.Modem.DialCommand = wvdial[dev]['Dial Command']

                if not wvdial[dev].has_key('Init1'):
                    wvdial[dev]['Init1'] = 'ATZ'
                hw.Modem.InitString =  wvdial[dev]['Init1']

                if not wvdial[dev].has_key('FlowControl'):
                    wvdial[dev]['FlowControl'] = CRTSCTS
                hw.Modem.FlowControl =  wvdial[dev]['FlowControl']

        self.commit() 
        self.setunmodified() 

    def save(self):
        self.commit() 

        modules = getMyConfModules(refresh = True)

        # cleanup isdnconf
        isdn = NCisdnhardware.ConfISDN()
        isdn.cleanup()

        for hw in self:
            hw.save()

        try:
            wvdial = getMyWvDial(create_if_missing = False)
        except:
            wvdial = None

        if wvdial:
            # Clean up wvdial
            for dev in wvdial.keys():
                if dev[:5] != 'Modem':
                    continue
                for hw in self:
                    if hw.Type == MODEM and hw.Name == dev:
                        break
                else:
                    # if the loop does not get interrupted by break
                    # we did not find the Modem in the hardwarelist
                    # and it gets deleted
                    del wvdial[dev]

        # FIXME: [198070] use modinfo to determine options
        # Clean up modules
        for mod in modules.keys():
            mtype = getDeviceType(mod)
            #
            # FIXME: This is not OO!!
            #
            if mtype != ETHERNET and mtype != TOKENRING and mtype != QETH:
                continue
            #print "Testing " + str(mod)
            for hw in self:
                if (hw.Type == ETHERNET or \
                    hw.Type == TOKENRING or hw.Type == QETH) and \
                    hw.Name == mod:
                    break
            else:
                #print "Removing " + str(mod)
                #print str(modules.vars[mod].keys())
                del modules[mod]
                #print "Test: " + str(modules[mod])


        modules.write()
        if wvdial:
            wvdial.write()

        self.commit() 
        self.setunmodified() 

__HWList = None
__HWList_root = getRoot()

def getHardwareList(refresh = None):
    # pylint: disable-msg=W0603
    global __HWList
    global __HWList_root

    if __HWList == None or refresh or \
           __HWList_root != getRoot():
        __HWList = HardwareList()
        __HWList.load()
        __HWList_root = getRoot()
    return __HWList

def getNextDev(base):
    hwlist = getHardwareList()
    num = 0
    for num in xrange(0, 100):
        for hw in hwlist:
            if hw.Name == base + str(num):
                break
        else:
            # no card seems to use this
            break
    # pylint: disable-msg=W0631
    return base + str(num)

__author__ = "Harald Hoyer <harald@redhat.com>"

