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
import os.path
from netconfpkg import NCDeviceList, NCIPsecList
from netconfpkg.NCDeviceList import ConfDevices
from netconfpkg.NCProfile import Profile
from netconfpkg.NC_functions import (_, log, SYSCONFNETWORK,
                                     getRoot, updateNetworkScripts,
                                     SYSCONFPROFILEDIR, OLDSYSCONFDEVICEDIR,
                                     RESOLVCONF, HOSTSCONF, TestError,
                                     SYSCONFDEVICEDIR, mkdir, issamefile, 
                                     unlink, link, rename, rmdir, 
                                     getTestEnv, generic_error_dialog, 
                                     generic_yesno_dialog, RESPONSE_YES)
from netconfpkg.conf import ConfShellVar, ConfEResolv
from netconfpkg.gdt import Gdtlist, gdtlist_properties


class ProfileList_base(Gdtlist):
    gdtlist_properties(Profile)

class MyFileList(list):
    def __setitem__(self, key, value):
        value = os.path.abspath(value)
        log.log(5, "MyFileList.__setitem__(self, %s, %s)" % (str(key), 
                                                             str(value)))
        return list.__setitem__(self, key, value)

    def __contains__(self, obj):
        obj = os.path.abspath(obj)
        ret = list.__contains__(self, os.path.abspath(obj))
        log.log(5, "MyFileList.__contains__(self, %s) == %s" 
                % (str(obj), str(ret)))
        return ret

    def append(self, obj):
        obj = os.path.abspath(obj)
        log.log(5, "MyFileList.append(self, %s)" % str(obj))
        return list.append(self, os.path.abspath(obj))

class ProfileList(ProfileList_base):
    def __init__(self):
        super(ProfileList, self).__init__()
        self.error = None

    def load(self):
        # pylint: disable-msg=W0201
        
        self.curr_prof = 'default'
        nwconf = ConfShellVar.ConfShellVar(getRoot() + SYSCONFNETWORK)
        if nwconf.has_key('CURRENT_PROFILE'):
            self.curr_prof = nwconf['CURRENT_PROFILE']

        if nwconf.has_key('HOSTNAME'):
            self.use_hostname = nwconf['HOSTNAME']
        else:
            self.use_hostname = 'localhost'

        if self.curr_prof == None or self.curr_prof == '':
            self.curr_prof = 'default'

        updateNetworkScripts()
        self.__delslice__(0, len(self))

        proflist = []
        if os.path.isdir(getRoot() + SYSCONFPROFILEDIR):
            proflist = os.listdir(getRoot() + SYSCONFPROFILEDIR)
            if proflist:
                for pr in proflist:
                    # 60016
                    profdir = getRoot() + SYSCONFPROFILEDIR + '/' + pr
                    if not os.path.isdir(profdir):
                        continue
                    self.loadprof(pr, profdir)                
            else:
                self.loadprof('default', None)
        else:
            self.loadprof('default', None)

        prof = self.getActiveProfile()
        log.log(5, "ActiveProfile: %s" % str(prof))        
        prof.DNS.Hostname = self.use_hostname
        self.commit()
        self.setunmodified()

    def loadprof(self, pr, profdir):
        
        devicelist = NCDeviceList.getDeviceList()
        ipseclist = NCIPsecList.getIPsecList()

        prof = Profile()
        self.append(prof)
        prof.ProfileName = pr

        if pr == self.curr_prof:
            prof.Active = True
        else:
            prof.Active = False

        devlist = []

        if profdir:
            devlist = ConfDevices(profdir)

        if not devlist:
            devlist = ConfDevices(getRoot() + OLDSYSCONFDEVICEDIR)

        for dev in devlist:
            for d in devicelist:
                if d.DeviceId == dev:
                    #print >> sys.stderr, "Appending ", d.DeviceId, dev
                    prof.ActiveDevices.append(dev)
                    break

        for ipsec in devlist:
            for d in ipseclist:
                if d.IPsecId == ipsec:
                    prof.ActiveIPsecs.append(ipsec)
                    break

        # CHECK: [198898] new backend for /etc/hosts        
        if profdir:
            try:
                prof.HostsList.load(filename = profdir + '/hosts')
            except ValueError, e:
                self.error = e.message
        else:
            try:
                prof.HostsList.load(filename = HOSTSCONF)
            except ValueError, e:
                self.error = e.message


        # FIXME: [183338] use SEARCH not resolv.conf
        dnsconf = ConfEResolv.ConfEResolv()
        if profdir:
            dnsconf.filename = profdir + '/resolv.conf'
        else:
            dnsconf.filename = getRoot() + RESOLVCONF
        dnsconf.read()
        prof.DNS.Hostname     = self.use_hostname
        prof.DNS.Domainname   = ''
        prof.DNS.PrimaryDNS   = ''
        prof.DNS.SecondaryDNS = ''
        prof.DNS.TertiaryDNS  = ''

        if profdir:
            nwconf = ConfShellVar.ConfShellVar(profdir + '/network')
        else:
            nwconf = ConfShellVar.ConfShellVar(getRoot() + SYSCONFNETWORK)

        if nwconf['HOSTNAME'] != '':
            prof.DNS.Hostname     = nwconf['HOSTNAME']
        if len(dnsconf['domain']) > 0:
            prof.DNS.Domainname   = dnsconf['domain'][0]
        if dnsconf.has_key('nameservers'):
            prof.DNS.PrimaryDNS = dnsconf['nameservers'][0]
            if len(dnsconf['nameservers']) > 1:
                prof.DNS.SecondaryDNS = dnsconf['nameservers'][1]
            if len(dnsconf['nameservers']) > 2:
                prof.DNS.TertiaryDNS = dnsconf['nameservers'][2]
        sl = prof.DNS.SearchList
        if dnsconf.has_key('search'):
            for ns in dnsconf['search']:
                sl.append(ns)

    def test(self):
        error = None
        for prof in self:
            try:
                prof.HostsList.test()
            except ValueError, e:
                if not error:
                    error = "Profile: %s \n%s" % (prof.ProfileName, e.message)
                else:
                    error += e.message
        if error:
            raise ValueError(error)
        #return
        # Keep that test for later versions
        devmap = {}
        devicelist = NCDeviceList.getDeviceList()

        for prof in self:
            if not prof.Active:
                continue
            for devId in prof.ActiveDevices:
                for dev in devicelist:
                    if dev.DeviceId == devId:
                        device = dev
                        break
                else:
                    continue

                if devmap.has_key(device.Device) and \
                       device.Alias == devmap[device.Device].Alias:
                    msg = (_('Device %s uses the same Hardware Device '
                             '"%s" like %s!\n') \
                          + _('Please select another Hardware Device or \n'
                              'activate only one of them.')) % \
                              (device.DeviceId, device.Device, \
                               devmap[device.Device].DeviceId)
                    raise TestError(msg)

                devmap[device.Device] = device
            break

    def fixInterfaces(self):
        return
#===============================================================================
#        pppnum = 0
#        ipppnum = 0
#        isdnnum = 0
#        devicelist = NCDeviceList.getDeviceList()
#        changed = 0
#        for prof in self:
#            if not prof.Active:
#                continue
#            for devid in prof.ActiveDevices:
#                for dev in devicelist:
#                    if dev.DeviceId != devid:
#                        continue
# 
#                    if dev.Type == MODEM or dev.Type == DSL:
#                        dstr = "ppp"+str(pppnum)
#                        if dev.Device != dstr:
#                            dev.Device = dstr
#                            changed = 1
#                        pppnum = pppnum + 1
#                    elif  dev.Type == ISDN:
#                        if dev.Dialup.EncapMode == 'syncppp':
#                            dstr = "ippp"+str(ipppnum)
#                            if dstr != dev.Device:
#                                dev.Device = dstr
#                                changed = 1
#                            if dev.Dialup.ChannelBundling == True:
#                                ipppnum = ipppnum + 1
#                                dstr = "ippp"+str(ipppnum)
#                                if dstr != dev.Dialup.SlaveDevice:
#                                    dev.Dialup.SlaveDevice = dstr
#                                    changed = 1
#                            ipppnum = ipppnum + 1
#                        else:
#                            dstr = "isdn"+str(isdnnum)
#                            if dstr != dev.Device:
#                                dev.Device = dstr
#                                changed = 1
#                            isdnnum = isdnnum + 1
#                    break
#            break
#===============================================================================

    def save(self):
        # FIXME: [163040] "Exception Occurred" when saving
        # fail gracefully, with informing, which file, and why
        import socket
        # Just to be safe...
        os.umask(0022)

        # commit the changes
        self.commit()

        nwconf = ConfShellVar.ConfShellVar(getRoot() + SYSCONFNETWORK)
        # FIXME: [183338] use SEARCH not resolv.conf
        dnsconf = ConfEResolv.ConfEResolv()

        act_prof = self.getActiveProfile()

        if(not getTestEnv() 
           and socket.gethostname() != act_prof.DNS.Hostname):
            if os.getuid() == 0:
                # FIXME: [169733] Renaming machine prevents 
                # applications from opening, if the hostname changed,
                # set it system wide (#55746)
                retval = generic_yesno_dialog(_(
                """You changed the hostname.

Should the hostname be set to the system now?
This may have the effect, that some X applications do not function properly.

You may have to relogin."""))
                if retval == RESPONSE_YES:
                    os.system("hostname %s" % act_prof.DNS.Hostname)
                    log.log(2, "change hostname to %s" % act_prof.DNS.Hostname)

            newip = '127.0.0.1'
            try:
                newip = socket.gethostbyname(act_prof.DNS.Hostname)
            except socket.error:
                for host in act_prof.HostsList:
                    if host.IP == '127.0.0.1' or host.IP == "::1":
                        host.Hostname = 'localhost.localdomain'
                        if 'localhost' not in host.AliasList:
                            host.AliasList.append('localhost')
                        # append the hostname to 127.0.0.1,
                        # if it does not contain a domain
                        if act_prof.DNS.Hostname.find(".") != -1:
                            host.AliasList.append(
                                    act_prof.DNS.Hostname.split(".")[0])
                        else:
                            host.AliasList.append(act_prof.DNS.Hostname)
            else:
                if newip != "127.0.0.1" and newip != "::1":
                    # We found an IP for the hostname
                    for host in act_prof.HostsList:
                        if host.IP == '127.0.0.1' or host.IP == "::1":
                            # reset localhost
                            host.Hostname = 'localhost.localdomain'
                            if 'localhost' not in host.AliasList:
                                host.AliasList.append('localhost')
                        if host.IP == newip:
                            # found entry in /etc/hosts with our IP
                            # change the entry
                            host.createAliasList()
                            try:
                                hname = socket.gethostbyaddr(newip)
                                host.Hostname = hname[0]
                                host.AliasList.extend(hname[1])
                            except socket.error:
                                host.Hostname = act_prof.DNS.Hostname
                                
                            if host.Hostname != act_prof.DNS.Hostname:
                                host.AliasList.append(act_prof.DNS.Hostname)
                            if act_prof.DNS.Hostname.find(".") != -1:
                                hname = act_prof.DNS.Hostname.split(".")[0]
                                if not hname in host.AliasList:
                                    host.AliasList.append(hname)

            #act_prof.HostsList.commit(changed=False)

        nwconf['HOSTNAME'] = act_prof.DNS.Hostname

        if act_prof.ProfileName != 'default':
            nwconf['CURRENT_PROFILE'] = act_prof.ProfileName
        else:
            del nwconf['CURRENT_PROFILE']

        nwconf.write()

        if not os.path.isdir(getRoot() + SYSCONFPROFILEDIR):
            mkdir(getRoot() + SYSCONFPROFILEDIR)

        files_used = MyFileList()

        for prof in self:
            if not os.path.isdir(getRoot() + SYSCONFPROFILEDIR + 
                                 '/' + prof.ProfileName):
                mkdir(getRoot() + SYSCONFPROFILEDIR + '/' + 
                      prof.ProfileName)
            files_used.append(getRoot() + SYSCONFPROFILEDIR + '/' + 
                              prof.ProfileName)

            nwconf = ConfShellVar.ConfShellVar(getRoot() + SYSCONFPROFILEDIR +
                                       '/' + prof.ProfileName + '/network')
#            print >> sys.stderr, "Writing Hostname ", 
#                    prof.ProfileName, prof.DNS.Hostname
            nwconf['HOSTNAME'] = prof.DNS.Hostname
            nwconf.write()
            files_used.append(nwconf.filename)


            # FIXME: [183338] use SEARCH not resolv.conf
            dnsconf.filename = getRoot() + SYSCONFPROFILEDIR + '/' + \
                               prof.ProfileName + '/resolv.conf'

            files_used.append(dnsconf.filename)

            dnsconf['domain'] = ''
            if prof.DNS.Domainname:
                dnsconf['domain'] = [prof.DNS.Domainname]
            else:
                del dnsconf['domain']

            dnsconf['search'] = []
            if prof.DNS.SearchList != []:
                dnsconf['search'] = prof.DNS.SearchList
            else:
                del dnsconf['search']

            dnsconf['nameservers'] = []
            nameservers = []
            if prof.DNS.PrimaryDNS:
                nameservers.append(prof.DNS.PrimaryDNS)
            if prof.DNS.SecondaryDNS:
                nameservers.append(prof.DNS.SecondaryDNS)
            if prof.DNS.TertiaryDNS:
                nameservers.append(prof.DNS.TertiaryDNS)

            dnsconf['nameservers'] = nameservers
            # CHECK: [198898] new backend for /etc/hosts
            filename = getRoot() + \
                SYSCONFPROFILEDIR + '/' + \
                prof.ProfileName + \
                '/hosts'
            prof.HostsList.save(filename=filename)
            files_used.append(filename)
            
            dnsconf.write()

            for devId in prof.ActiveDevices:
                for prefix in [ 'ifcfg-', 'route-', 'keys-']:
                    devfilename = getRoot() + SYSCONFDEVICEDIR + \
                                  prefix + devId
                    profilename = getRoot() + SYSCONFPROFILEDIR + '/' + \
                                  prof.ProfileName + '/' + prefix + devId

                    if os.path.isfile(devfilename):
                        if not issamefile(devfilename, profilename):
                            unlink(profilename)
                            link(devfilename, profilename)

                        files_used.append(devfilename)
                        files_used.append(profilename)

                # unlink old .route files
                profilename = getRoot() + SYSCONFPROFILEDIR + '/' + \
                              prof.ProfileName + '/' + devId + '.route'
                unlink(profilename)


                if prof.Active == False and prof.ProfileName != 'default':
                    continue

                # Active Profile or default profile
                for prefix in [ 'ifcfg-', 'route-', 'keys-' ]:
                    devfilename = getRoot() + SYSCONFDEVICEDIR + \
                                      '/' + prefix + devId
                    profilename = getRoot() + OLDSYSCONFDEVICEDIR + \
                                  '/' + prefix + devId

                    if os.path.isfile(devfilename):
                        if not issamefile(devfilename, profilename):
                            unlink(profilename)
                            link(devfilename, profilename)
                        files_used.append(profilename)

                # unlink old .route files
                unlink(getRoot() + OLDSYSCONFDEVICEDIR + \
                       '/' + devId + '.route')

            for devId in prof.ActiveIPsecs:
                for prefix in [ 'ifcfg-', 'keys-']:
                    devfilename = getRoot() + SYSCONFDEVICEDIR + \
                                  prefix + devId
                    profilename = getRoot() + SYSCONFPROFILEDIR + '/' + \
                                  prof.ProfileName + '/' + prefix + devId

                    if os.path.isfile(devfilename):
                        if not issamefile(devfilename, profilename):
                            unlink(profilename)
                            link(devfilename, profilename)

                        files_used.append(devfilename)
                        files_used.append(profilename)

                if prof.Active == False and prof.ProfileName != 'default':
                    continue

                # Active Profile or default profile
                for prefix in [ 'ifcfg-', 'keys-' ]:
                    devfilename = getRoot() + SYSCONFDEVICEDIR + \
                                      '/' + prefix + devId
                    profilename = getRoot() + OLDSYSCONFDEVICEDIR + \
                                  '/' + prefix + devId

                    if os.path.isfile(devfilename):
                        if not issamefile(devfilename, profilename):
                            unlink(profilename)
                            link(devfilename, profilename)

                        files_used.append(profilename)

            if prof.Active == False:
                continue

            # Special actions for the active profile

            for (mfile, cfile) in { RESOLVCONF : '/resolv.conf',
                                    HOSTSCONF : '/hosts' }.items():
                hostfile = getRoot() + mfile
                conffile = getRoot() + SYSCONFPROFILEDIR + '/' + \
                           prof.ProfileName + cfile
                if(os.path.isfile(conffile) 
                   and (not os.path.isfile(hostfile) 
                        or not issamefile(hostfile, conffile))):
                    rename(hostfile, hostfile + '.bak')
                    unlink(hostfile)
                    link(conffile, hostfile)

                os.chmod(hostfile, 0644)

        # Remove all unused files that are linked in the device directory
        devlist = os.listdir(getRoot() + OLDSYSCONFDEVICEDIR)
        for dev in devlist:
            if dev.split('-')[0] not in [ 'ifcfg', 'route', 
                                                  'keys' ] or \
                                                  (len(dev) > 6 and \
                                                   dev[-6:] == '.route') \
                                                  or dev == 'ifcfg-lo':
                continue
            mfile = getRoot() + OLDSYSCONFDEVICEDIR+'/'+dev
            if mfile in files_used:
                # Do not remove used files
                continue
            try:
                stat = os.stat(mfile)
                if stat[3] > 1:
                    # Check, if it is a device of neat 
                    # in every profile directory
                    dirlist = os.listdir(getRoot() + SYSCONFPROFILEDIR)
                    for mdir in dirlist:
                        dirname = getRoot() + SYSCONFPROFILEDIR + '/' + mdir
                        if not os.path.isdir(dirname):
                            continue
                        filelist = os.listdir(dirname)
                        for file2 in filelist:
                            stat2 = os.stat(dirname + '/' + file2)
                            if os.path.samestat(stat, stat2):
                                unlink(mfile)
            except OSError, e:
                generic_error_dialog(
                        _("Error removing file %(file)s: %(errormsg)")
                        % { "file" : mfile, "errormsg" : str(e) } )


        # Remove all profile directories except default
        proflist = os.listdir(getRoot() + SYSCONFPROFILEDIR)
        for prof in proflist:
            # Remove all files in the profile directory
            filelist = os.listdir(getRoot() + SYSCONFPROFILEDIR + prof)
            for mfile in filelist:
                filename = getRoot() + SYSCONFPROFILEDIR + prof + '/' + \
                           mfile
                if filename in files_used:
                    # Do not remove used files
                    log.log(6, "%s not removed" % filename)
                    continue
                unlink(filename)

            filename = getRoot() + SYSCONFPROFILEDIR + prof
            if not (filename in files_used):
                rmdir(filename)

        # commit the changes
        self.commit()
        self.setunmodified() 

    def activateDevice (self, deviceid, profile, state=None):
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.ProfileName != profile:
                continue
            if state:
                if deviceid not in prof.ActiveDevices:
                    prof.ActiveDevices.append(deviceid)
            else:
                if deviceid in prof.ActiveDevices:
                    del prof.ActiveDevices[prof.ActiveDevices.index(deviceid)]

    def activateIpsec (self, ipsecid, profile, state=None):
        profilelist = getProfileList()

        for prof in profilelist:
            if prof.ProfileName != profile:
                continue
            if state:
                if ipsecid not in prof.ActiveIPsecs:
                    prof.ActiveIPsecs.append(ipsecid)
            else:
                if ipsecid in prof.ActiveIPsecs:
                    del prof.ActiveIPsecs[prof.ActiveIPsecs.index(ipsecid)]

    def switchToProfile(self, val, dochange = True):
        aprof = None
        for prof in self:
            if (isinstance(val, str) and prof.ProfileName == val) or \
                   (isinstance(val, Profile) and prof == val) :
                break
        else:
            return None

        modl = self.modified() 
        for prof in self:
            mod = prof.modified()
            if (isinstance(val, str) and prof.ProfileName == val) or \
                   (isinstance(val, Profile) and prof == val) :
                prof.Active = True
                aprof = prof
            else:
                prof.Active = False
            #if not dochange:
            #    prof.setunmodified(mod)

        #if not dochange:
        #    self.setunmodified(modl) 

        return aprof

    def getActiveProfile(self):
        for prof in self:
            if not prof.Active:
                continue
            return prof

        if len(self):
            self[0].Active = True
            return self[0]

    def tostr(self, prefix_string = None):
        "returns a string in gdt representation"
        #print "tostr %s " % prefix_string
        if prefix_string == None:
            prefix_string = self.__class__.__name__
        mstr = ""
        for value in self:
            if isinstance(value, Profile):
                mstr += value.tostr("%s.%s" 
                                    % (prefix_string, value.ProfileName))
        return mstr


    def fromstr(self, vals, value):
        # pylint: disable-msg=W0212
        if len(vals) <= 1:
            return
        if vals[0] == "ProfileList":
            del vals[0]
        else:
            return
        for profile in self:
            if profile.ProfileName == vals[0]:
                profile.fromstr(vals[1:], value)
                return

        prof = Profile()
        self.append(prof)
        prof.ProfileName = vals[0]
        prof.fromstr(vals[1:], value)


__PFList = None
__PFList_root = getRoot()

def getProfileList(refresh=None):
    # pylint: disable-msg=W0603
    global __PFList
    global __PFList_root

    if __PFList == None or refresh or \
           __PFList_root != getRoot():
        __PFList = ProfileList()
        __PFList.load()
        __PFList_root = getRoot()
    return __PFList

__author__ = "Harald Hoyer <harald@redhat.com>"
