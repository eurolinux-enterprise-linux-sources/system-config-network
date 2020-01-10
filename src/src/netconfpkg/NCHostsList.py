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
from netconfpkg.NCHost import Host
from netconfpkg.gdt import Gdtlist, gdtlist_properties


def _saveEntry(entry, conffile):
    if isinstance(entry, str):
        conffile.write(entry + "\n")
    elif isinstance(entry, Host):
        if ((not entry.modified()) 
            and hasattr(entry, "origLine")
            and entry.origLine):
            conffile.write(entry.origLine+"\n")
            return
        if entry.IP:
            conffile.write(entry.IP)
        if entry.Hostname:
            conffile.write("\t" + entry.Hostname)
        if entry.AliasList:
            for alias in entry.AliasList:
                conffile.write("\t" + alias)
        if hasattr(entry, "Comment") and entry.Comment:
            conffile.write(" #" + entry.Comment)

        conffile.write("\n")

class HostsList_base(Gdtlist):
    "HostsList base class"
    gdtlist_properties(Host)
    
class HostsList(HostsList_base):
    "HostsList class"
    
    def test(self):
        error = None
        num = 0
        for host in self:
            num += 1
            if isinstance(host, Host):
                try:
                    host.test()
                except ValueError, value_exception:
                    if not error:
                        error = """\
Error in hostslist
Wrong: %s in entry %i
""" % (value_exception.message, num)
                    else:
                        error += "Wrong: %s in entry %i\n" \
                            % (value_exception.message, num)
        if error:
            raise ValueError(error)
    
    def load(self, filename='/etc/hosts'):
        try:
            conffile = open(filename, 'r')
            lines = conffile.readlines()
            conffile.close()
        except:
            return
        num = 0
        error = None
        badlines = []
        for line in lines:
            num += 1
            line = line.strip()
            tmp = line.partition('#')
            comment = tmp[2]
            tmp = tmp[0].split()
            
            # if the line contains more than comment we 
            # suppose that it's ip with Aliases
            if len(tmp) > 0:
                entry = Host()
                entry.IP = tmp[0]
                entry.Comment = comment.rstrip()
                if len(tmp) > 1:
                    entry.Hostname = tmp[1]
                    for alias in tmp[2:]:
                        entry.AliasList.append(alias)
                entry.origLine = line
                # catch invalid entry in /etc/hosts
                try:
                    entry.test()
                except ValueError, value_exception:
                    badlines.append((num, value_exception.message))
                    if not error:
                        error = """\
Error while parsing /etc/hosts:
Wrong %s on line %i
""" % (value_exception.message, num)                    
                    else:
                        error += "Wrong %s on line %i\n" \
                            % (value_exception.message, num)
            else:
                entry = line

            # add every line to configuration
            self.append(entry) 
        if error:
            value_exception = ValueError(error)
            value_exception.badlines = badlines
            raise value_exception
        self.commit()
        self.setunmodified()
        
    def __iter__(self):
        """
        Replace __iter__ for backwards compatibility. 
        Returns only valid Host objects
        """
#        return iter(filter(lambda x: isinstance(x, Host), 
#                           HostsList_base.__iter__(self)))
        return iter([x for x in super(HostsList, self).__iter__()
                     if isinstance(x, Host)])


    def save(self, mfile = None, filename = None):
        if filename:            
            conffile = open(filename, "w")
        elif mfile:
            conffile = mfile
        else:
            conffile = open("/etc/hosts", "w")

        for entry in super(HostsList, self).__iter__():
            #print >> sys.stderr, entry
            _saveEntry(entry, conffile)
            
        if mfile:
            conffile.close()

    def fromstr(self, vals, value):
        if vals[0] == "HostsList":
            del vals[0]

        for host in self:
            if host.HostID == vals[0]:
                host.fromstr(vals[1:], value)
                return
        host = Host()
        self.append(host) 
        host.HostID = vals[0]
        host.fromstr(vals[1:], value)
